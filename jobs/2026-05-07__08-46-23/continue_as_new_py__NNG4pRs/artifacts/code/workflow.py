from datetime import timedelta
from temporalio import workflow

@workflow.defn
class ProcessItemsWorkflow:
    @workflow.run
    async def run(self, start_index: int, total_items: int) -> bool:
        processed_count = 0
        current_index = start_index

        while current_index < total_items:
            # Simulate processing an item
            await workflow.sleep(timedelta(milliseconds=1))
            processed_count += 1
            current_index += 1

            if processed_count == 100 and current_index < total_items:
                workflow.continue_as_new(current_index, total_items)

        return True
