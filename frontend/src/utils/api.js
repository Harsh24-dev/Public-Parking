export async function authorizedFetch(url, options = {}){
    const token = localStorage.getItem('auth_token');

    if (!token){
        console.error('No auth token found. User may not logged in.');
        throw new Error('No auth token found');
    }

    const mheaders = {
        'Content-Type': 'application/json',
        'Authentication-Token': token,
    };

    // Merge custom headers from options if any
    const mergedHeaders = {
        ...mheaders,
        ...(options.headers || {})
    };
    // Build final fetch config
    const config = {
        ...options,
        headers: mergedHeaders,
        credentials: 'include',
        };

    try{
        const response = await fetch(url, config);

        if (!response.ok){
            console.warn(`Fetch returned HTTP ${response.status}: ${response.statusText}`);
            throw new Error(`Http error! status: $(response.status)`);
        }
        return response;
    } catch (error) {
        console.error('fetch failed:', error);
        throw error;
    }
}