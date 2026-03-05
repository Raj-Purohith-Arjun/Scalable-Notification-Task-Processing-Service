import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_process_job_completed():
    from worker.worker import process_job

    mock_db = AsyncMock()
    mock_db.__aenter__ = AsyncMock(return_value=mock_db)
    mock_db.__aexit__ = AsyncMock(return_value=False)

    with patch("worker.worker.AsyncSessionLocal", return_value=mock_db), \
         patch("worker.worker.update_task_status", new_callable=AsyncMock) as mock_update, \
         patch("worker.worker.create_notification", new_callable=AsyncMock) as mock_notify, \
         patch("asyncio.sleep", new_callable=AsyncMock):

        await process_job({"task_id": "00000000-0000-0000-0000-000000000001", "title": "test"})

        calls = [c.args[1] for c in mock_update.call_args_list]
        assert "processing" in calls
        assert "completed" in calls
        mock_notify.assert_called_once()


@pytest.mark.asyncio
async def test_process_job_failed():
    from worker.worker import process_job

    mock_db = AsyncMock()
    mock_db.__aenter__ = AsyncMock(return_value=mock_db)
    mock_db.__aexit__ = AsyncMock(return_value=False)

    async def raise_on_complete(task_id, status, db):
        if status == "processing":
            raise RuntimeError("db error")

    with patch("worker.worker.AsyncSessionLocal", return_value=mock_db), \
         patch("worker.worker.update_task_status", side_effect=raise_on_complete), \
         patch("worker.worker.create_notification", new_callable=AsyncMock):

        # should not raise
        await process_job({"task_id": "00000000-0000-0000-0000-000000000002", "title": "fail"})
