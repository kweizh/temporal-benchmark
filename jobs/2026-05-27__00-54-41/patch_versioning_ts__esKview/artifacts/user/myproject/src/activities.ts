import * as fs from 'fs';

const ORDER_LOG = '/workspace/order.log';
const NOTIFY_LOG = '/workspace/notify.log';

export async function chargeCard(orderId: string): Promise<void> {
  await new Promise((r) => setTimeout(r, 1000));
  fs.appendFileSync(ORDER_LOG, `charged:${orderId}\n`);
}

export async function shipOrder(orderId: string): Promise<void> {
  await new Promise((r) => setTimeout(r, 1000));
  fs.appendFileSync(ORDER_LOG, `shipped:${orderId}\n`);
}

export async function notifyCustomer(orderId: string): Promise<void> {
  await new Promise((r) => setTimeout(r, 500));
  fs.appendFileSync(NOTIFY_LOG, `notified:${orderId}\n`);
}
