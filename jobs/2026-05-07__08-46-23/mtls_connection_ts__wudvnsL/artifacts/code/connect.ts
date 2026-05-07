import { Connection } from '@temporalio/client';
import { loadClientConnectConfig } from '@temporalio/envconfig';

async function run() {
  try {
    const config = await loadClientConnectConfig({
      profile: 'prod',
      configSource: { path: './config.toml' },
    });

    // connectionOptions will include address and tls settings loaded from config.toml
    await Connection.connect(config.connectionOptions);
    console.log('Connected successfully (unexpectedly!)');
  } catch (err) {
    console.log('Connection failed as expected');
  }
}

run().catch((err) => {
  console.error('An unexpected error occurred:', err);
  process.exit(1);
});
