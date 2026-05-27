"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const client_main_1 = require("./client-main");
(0, client_main_1.main)().catch((err) => {
    console.error('Client failed:', err);
    process.exit(1);
});
//# sourceMappingURL=client.js.map