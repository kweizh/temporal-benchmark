export async function chargeCustomer(orderId: string): Promise<string> {
  return `charged v1 ${orderId}`;
}
export async function chargeCustomerV2(orderId: string): Promise<string> {
  return `charged v2 ${orderId}`;
}
