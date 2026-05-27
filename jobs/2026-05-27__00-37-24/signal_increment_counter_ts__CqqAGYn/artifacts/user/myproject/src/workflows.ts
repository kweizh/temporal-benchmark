import { defineSignal, setHandler, condition } from '@temporalio/workflow';

export const incrementSignal = defineSignal<[number]>('increment');
export const finishSignal = defineSignal('finish');

export async function CounterWorkflow(): Promise<number> {
  let counter = 0;
  let isDone = false;

  setHandler(incrementSignal, (amount: number) => {
    counter += amount;
  });

  setHandler(finishSignal, () => {
    isDone = true;
  });

  await condition(() => isDone);
  return counter;
}
