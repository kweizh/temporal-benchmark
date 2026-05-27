import { defineSignal, setHandler, condition } from '@temporalio/workflow';

// Define signals
export const incrementSignal = defineSignal<[number]>('increment');
export const finishSignal = defineSignal('finish');

export async function CounterWorkflow(): Promise<number> {
  let counter = 0;
  let done = false;

  // Handle increment signal: add the given value to the counter
  setHandler(incrementSignal, (value: number) => {
    counter += value;
  });

  // Handle finish signal: set the done flag
  setHandler(finishSignal, () => {
    done = true;
  });

  // Block until the finish signal sets done = true
  await condition(() => done);

  return counter;
}
