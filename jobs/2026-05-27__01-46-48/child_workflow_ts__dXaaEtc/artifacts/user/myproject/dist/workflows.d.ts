/**
 * DoubleWorkflow accepts a single number `n` and returns `n * 2`.
 */
export declare function DoubleWorkflow(n: number): Promise<number>;
/**
 * ParentSumWorkflow accepts an array of numbers, invokes DoubleWorkflow
 * once per element via executeChild, and returns the sum of all doubled values.
 */
export declare function ParentSumWorkflow(numbers: number[]): Promise<number>;
//# sourceMappingURL=workflows.d.ts.map