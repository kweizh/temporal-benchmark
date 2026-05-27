import { main } from './client-main';

main().catch((err) => {
  console.error('Client failed:', err);
  process.exit(1);
});
