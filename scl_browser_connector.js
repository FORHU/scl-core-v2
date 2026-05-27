/**
 * SCLBrowserConnector.js
 * Browser-native wrapper for SCL Core WebSocket API.
 */

class SCLBrowserConnector {
    constructor(host = "http://127.0.0.1:8000") {
        this.host = host.replace(/\/$/, "");
        this.wsUrl = this.host.replace(/^http/, 'ws') + "/chat-stream";
    }

    async createSession() {
        try {
            const response = await fetch(`${this.host}/session-id`);
            if (!response.ok) throw new Error("Failed to create session");
            const data = await response.json();
            return data.session_id;
        } catch (err) {
            console.error("[SCL] Session Error:", err);
            throw err;
        }
    }

    async runCase(label, query, callbacks = {}, options = {}) {
        const {
            onChunk = (delta) => {},
            onPendingApproval = async (payload) => { return "approved"; },
            onComplete = (summary) => {},
            onError = (err) => {}
        } = callbacks;

        const sessionId = options.session_id || await this.createSession();

        return new Promise((resolve, reject) => {
            const socket = new WebSocket(this.wsUrl);
            let fullText = "";

            socket.onopen = () => {
                console.log(`[SCL] Connected: ${label}`);
                socket.send(JSON.stringify({
                    type: "chat",
                    session_id: sessionId,
                    user_input: query,
                    language: options.language || "English",
                    ...options
                }));
            };

            socket.onmessage = async (event) => {
                const message = event.data;
                if (message === "__END__") {
                    socket.close();
                    return resolve(fullText);
                }

                const payload = JSON.parse(message);
                const type = payload.type || payload.status;

                switch (type) {
                    case "chunk":
                        fullText += payload.delta;
                        onChunk(payload.delta);
                        break;
                    case "pending_approval":
                        const decision = await onPendingApproval(payload);
                        socket.send(JSON.stringify({
                            type: "approve",
                            session_id: sessionId,
                            decision: decision,
                            comments: "Decision via Browser UI"
                        }));
                        break;
                    case "complete":
                        onComplete(payload);
                        break;
                    case "error":
                        onError(payload.error);
                        socket.close();
                        reject(payload.error);
                        break;
                }
            };
            socket.onerror = (err) => { onError(err); reject(err); };
        });
    }
}
