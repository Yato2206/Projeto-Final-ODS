import { getErrorDescription } from "./errorDescriptions";

const API_BASE_URL = "/api";

class ApiError extends Error {
    constructor(public status: number, message: string) {
        super(message);
    }
}

export async function fetchApi<T>(
    endpoint: string,
    options: RequestInit = {}
): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...options.headers,
        },
    });

    if (!response.ok) {
        const error = await response
            .json()
            .catch(() => ({ title: "Unknown error" }));
        const errorMessage = error.title
            ? getErrorDescription(error.title)
            : response.statusText;
        throw new ApiError(response.status, errorMessage);
    }

    if (response.status === 204) {
        return undefined as T;
    }

    return response.json();
}

export const api = {

}

export { ApiError };