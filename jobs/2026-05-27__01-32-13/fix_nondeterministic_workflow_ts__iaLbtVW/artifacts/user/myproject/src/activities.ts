// Define Temporal Activity functions here.
//
// The Workflow in `./workflows.ts` is expected to call an Activity called
// `pickDiscount()` that returns one of [0, 5, 10, 15, 20] chosen at random.
//
// Activities may freely use non-deterministic APIs such as `Math.random`,
// `Date`, network calls, and database access.

export async function healthCheck(): Promise<string> {
  return 'ok';
}

export async function pickDiscount(): Promise<number> {
  const options = [0, 5, 10, 15, 20];
  const idx = Math.floor(Math.random() * options.length);
  return options[idx];
}
