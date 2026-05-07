export async function chargeUser(tier: string): Promise<string> {
  return `Charged for ${tier}`;
}
