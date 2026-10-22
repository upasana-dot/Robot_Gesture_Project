
import time

from app.ai.planner import generate_plan
from app.database import SessionLocal
from app.models import Task, ActionStep
from app.planning.validator import validate_plan
from app.simulation.executor import TaskExecutor
from app.simulation.world import RobotWorld


def create_and_execute_task(instruction, db):
    # 1. Generate and validate the action plan.
    raw_actions = generate_plan(instruction)
    actions = validate_plan(raw_actions)

    # 2. Save the task and planned actions.
    task = Task(
        instruction=instruction,
        status="planned",
    )
    db.add(task)
    db.flush()

    for action in actions:
        db.add(
            ActionStep(
                task_id=task.id,
                **action,
                status="pending",
            )
        )

    db.commit()
    db.refresh(task)

    # 3. Start simulation and execute the actions.
    task.status = "running"
    db.commit()

    world = None
    results = []
    start_time = time.perf_counter()

    try:
        world = RobotWorld(gui=False)
        executor = TaskExecutor(world)
        results = executor.execute(actions)

    except Exception as exc:
        results = [
            {
                "action": "execution",
                "success": False,
                "error": str(exc),
            }
        ]

    finally:
        if world is not None:
            world.close()

    # 4. Save each action's execution status.
    for index, action_record in enumerate(task.actions):
        if index < len(results):
            result = results[index]
            action_record.status = (
                "completed" if result.get("success") else "failed"
            )
            action_record.error_message = result.get("error")
        else:
            action_record.status = "skipped"
            action_record.error_message = (
                "Not executed because an earlier step failed."
            )

    all_successful = (
        len(results) == len(actions)
        and all(result.get("success", False) for result in results)
    )

    task.status = "completed" if all_successful else "failed"

    if task.actions:
        task.actions[-1].duration_seconds = round(
            time.perf_counter() - start_time, 3
        )

    db.commit()
    db.refresh(task)

    # 5. Return the task and execution results.
    return {
        "task_id": task.id,
        "instruction": task.instruction,
        "status": task.status,
        "actions": [
            {
                "step_number": action.step_number,
                "action": action.action,
                "object_name": action.object_name,
                "target": action.target,
                "status": action.status,
                "error_message": action.error_message,
                "duration_seconds": action.duration_seconds,
            }
            for action in task.actions
        ],
        "execution_results": results,
    }
