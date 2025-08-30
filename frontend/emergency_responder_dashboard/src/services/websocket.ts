// Types
interface WebSocketMessage {
  type: string;
  payload: any;
}

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectTimeout = 5000; // 5 seconds
  private messageHandlers: Map<string, ((payload: any) => void)[]> = new Map();

  constructor(private url: string = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws') {}

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    this.ws = new WebSocket(this.url);

    this.ws.onopen = this.handleOpen.bind(this);
    this.ws.onmessage = this.handleMessage.bind(this);
    this.ws.onerror = this.handleError.bind(this);
    this.ws.onclose = this.handleClose.bind(this);
  }

  private handleOpen(): void {
    console.log('WebSocket connection established');
    this.reconnectAttempts = 0;
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);
      const handlers = this.messageHandlers.get(message.type);
      
      if (handlers) {
        handlers.forEach(handler => handler(message.payload));
      }
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  }

  private handleError(error: Event): void {
    console.error('WebSocket error:', error);
  }

  private handleClose(): void {
    console.log('WebSocket connection closed');
    
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => this.connect(), this.reconnectTimeout);
    } else {
      console.error('Max reconnection attempts reached');
    }
  }

  subscribe(type: string, handler: (payload: any) => void): () => void {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, []);
    }

    const handlers = this.messageHandlers.get(type)!;
    handlers.push(handler);

    // Return unsubscribe function
    return () => {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    };
  }

  send(type: string, payload: any): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      const message: WebSocketMessage = { type, payload };
      this.ws.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not connected');
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.messageHandlers.clear();
  }
}

export const wsService = new WebSocketService();

// Event types
export const WS_EVENTS = {
  DISASTER: {
    UPDATE: 'disaster:update',
    NEW: 'disaster:new',
    STATUS_CHANGE: 'disaster:status'
  },
  EMERGENCY: {
    NEW: 'emergency:new',
    STATUS_UPDATE: 'emergency:status'
  },
  RESOURCE: {
    UPDATE: 'resource:update',
    ALLOCATION: 'resource:allocate'
  },
  ALERT: {
    NEW: 'alert:new',
    UPDATE: 'alert:update'
  }
};
