export const useSessionId = () => {
    const session = localStorage.getItem('sessionId');
    if (!session) {
        const newSessionId = crypto.randomUUID();
        localStorage.setItem('sessionId', newSessionId);
        return newSessionId;
    }
    return session;
};