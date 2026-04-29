export const errorDescriptions: Record<string, string> = {

};

export function getErrorDescription(errorType: string): string {
    return errorDescriptions[errorType] || errorType;
}