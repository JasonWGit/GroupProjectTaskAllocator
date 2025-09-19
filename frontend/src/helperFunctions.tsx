const BACKEND_URL = "http://localhost:8000";

interface Options {
    method: string,
    body?: string
    headers?: Record<string, string>;
}

const fetchFromBackend = async (path: string, method: string, body: any | null = null) => {
    const options: Options = {
        method: method,
        headers: { "Content-Type": "application/json" }
    }

    if (body != null && method != "GET") {
        options.body = JSON.stringify(body);
    }
    const response = await fetch(BACKEND_URL + path, options);

    if (!response.ok) {
        try {
            const errorData = await response.json();
            throw new Error(`HTTP Error on fetch: code: ${response.status}, msg: ${errorData.error}`);
        } catch (err) {
            throw err;
        } 
    }

    return response.json();
}

export default fetchFromBackend;