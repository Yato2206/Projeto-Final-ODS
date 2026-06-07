export async function getNumberDocs(): Promise<number> {
        const response = await fetch(`index.json`);
        const data = await response.json();
        return data.count || 0;
    }