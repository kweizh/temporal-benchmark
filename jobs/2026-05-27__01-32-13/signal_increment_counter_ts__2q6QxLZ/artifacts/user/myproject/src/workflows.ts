import { condition, defineSignal, setHandler } from "@temporalio/workflow";

export const incrementSignal = defineSignal<[number]>("increment");
export const finishSignal = defineSignal("finish");

export async function CounterWorkflow(): Promise<number> {
  let counter = 0;
  let done = false;

  setHandler(incrementSignal, (value) => {
    counter += value;
  });

  setHandler(finishSignal, () => {
    done = true;
  });

  await condition(() => done);
  return counter;
}
