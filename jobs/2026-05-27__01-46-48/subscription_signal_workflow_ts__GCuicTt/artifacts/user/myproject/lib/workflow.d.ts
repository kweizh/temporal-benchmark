export declare const upgradeSignal: import("@temporalio/workflow").SignalDefinition<[string], string>;
export declare const cancelSignal: import("@temporalio/workflow").SignalDefinition<[], "cancel">;
export declare const getStatusQuery: import("@temporalio/workflow").QueryDefinition<{
    tier: string;
    billings: number;
    cancelled: boolean;
}, [], string>;
export interface SubscriptionInput {
    userId: string;
    tier: string;
}
export interface SubscriptionResult {
    billings: number;
    finalTier: string;
    cancelled: boolean;
}
export declare function SubscriptionWorkflow(input: SubscriptionInput): Promise<SubscriptionResult>;
//# sourceMappingURL=workflow.d.ts.map