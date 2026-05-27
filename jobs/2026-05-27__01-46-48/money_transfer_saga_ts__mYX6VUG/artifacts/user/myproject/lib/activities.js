"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.withdraw = withdraw;
exports.deposit = deposit;
exports.refund = refund;
const activity_1 = require("@temporalio/activity");
const fs = __importStar(require("fs"));
const ACCOUNTS_FILE = '/workspace/accounts.json';
/**
 * Read the accounts JSON, apply a mutation, then write it back atomically.
 */
function mutateAccounts(fn) {
    // Read
    const raw = fs.readFileSync(ACCOUNTS_FILE, 'utf8');
    const accounts = JSON.parse(raw);
    // Mutate
    fn(accounts);
    // Write (overwrite in place; this is single-process so no locking needed)
    fs.writeFileSync(ACCOUNTS_FILE, JSON.stringify(accounts, null, 2), 'utf8');
}
/**
 * Subtract `amount` from `accounts[account]`.
 */
async function withdraw(account, amount) {
    console.log(`[activity] withdraw: account=${account} amount=${amount}`);
    mutateAccounts((accounts) => {
        const current = accounts[account] ?? 0;
        accounts[account] = current - amount;
    });
    console.log(`[activity] withdraw complete`);
}
/**
 * Add `amount` to `accounts[account]`.
 * If `account === "B_FAIL"`, throw a non-retryable error to simulate failure.
 */
async function deposit(account, amount) {
    console.log(`[activity] deposit: account=${account} amount=${amount}`);
    if (account === 'B_FAIL') {
        // Non-retryable: mark as non-retryable so Temporal honours maximumAttempts=1
        throw activity_1.ApplicationFailure.nonRetryable(`Deposit to account "${account}" is not allowed (simulated failure)`, 'DepositFailed');
    }
    mutateAccounts((accounts) => {
        const current = accounts[account] ?? 0;
        accounts[account] = current + amount;
    });
    console.log(`[activity] deposit complete`);
}
/**
 * Add `amount` back to `accounts[account]` — reverses a prior withdraw.
 */
async function refund(account, amount) {
    console.log(`[activity] refund: account=${account} amount=${amount}`);
    mutateAccounts((accounts) => {
        const current = accounts[account] ?? 0;
        accounts[account] = current + amount;
    });
    console.log(`[activity] refund complete`);
}
//# sourceMappingURL=activities.js.map