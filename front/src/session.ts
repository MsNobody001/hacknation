const SESSION_KEY = 'sessionId';

export const hasSession = () => {
    return !!localStorage.getItem(SESSION_KEY);
}

export const initSession = () => {
    const newSessionId = crypto.randomUUID();
    localStorage.setItem(SESSION_KEY, newSessionId);
    return newSessionId;
};

export const useSessionId = () => {
    const session = localStorage.getItem(SESSION_KEY);
    if (!session) return initSession();
    return session;
};