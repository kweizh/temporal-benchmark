export interface ReminderInput {
    message: string;
    delaySeconds: number;
}
/**
 * ReminderWorkflow: sleeps for delaySeconds, then calls Notify and returns its result.
 */
export declare function ReminderWorkflow(input: ReminderInput): Promise<string>;
//# sourceMappingURL=workflows.d.ts.map