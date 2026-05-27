// Define Temporal Activity functions here.
//
// Activities may freely use non-deterministic APIs such as `Math.random`,
// `Date`, network calls, and database access.

export async function healthCheck(): Promise<string> {
  return 'ok';
}

// pickDiscount randomly selects one of the allowed discount percentages.
// Because this runs inside an Activity (not inside Workflow code), using
// Math.random() here is perfectly safe and replay-deterministic.
export async function pickDiscount(): Promise<number> {
  const options = [0, 5, 10, 15, 20];
  const idx = Math.floor(Math.random() * options.length);
  return options[idx];
}
