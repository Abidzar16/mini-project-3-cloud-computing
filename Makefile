.PHONY: help setup start stop restart logs clean install publisher subscriber status dashboard

# Default target
help:
	@echo "╔════════════════════════════════════════════════════════════╗"
	@echo "║         IoT Monitoring System - Make Commands             ║"
	@echo "╚════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make setup          - Setup environment and install dependencies"
	@echo "  make install        - Install Python dependencies"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make start          - Start all Docker services"
	@echo "  make stop           - Stop all Docker services"
	@echo "  make restart        - Restart all Docker services"
	@echo "  make status         - Show status of all services"
	@echo "  make logs           - Show logs from all services"
	@echo ""
	@echo "Application Commands:"
	@echo "  make run            - Run both publisher and subscriber"
	@echo "  make publisher      - Run publisher only (foreground)"
	@echo "  make subscriber     - Run subscriber only (foreground)"
	@echo "  make run-bg         - Run publisher and subscriber in background"
	@echo "  make stop-apps      - Stop background publisher and subscriber"
	@echo ""
	@echo "Monitoring Commands:"
	@echo "  make dashboard      - Open Grafana dashboard in browser"
	@echo "  make hivemq         - Open HiveMQ Control Center in browser"
	@echo "  make influxdb       - Open InfluxDB UI in browser"
	@echo "  make restart-grafana- Restart Grafana (fix dashboard issues)"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make clean          - Stop services and remove containers"
	@echo "  make clean-all      - Clean everything including volumes (⚠️  DATA LOSS)"
	@echo "  make logs-pub       - Show publisher logs"
	@echo "  make logs-sub       - Show subscriber logs"
	@echo ""

# Setup environment
setup: install
	@echo "📝 Setting up environment..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✓ Created .env file from .env.example"; \
	else \
		echo "✓ .env file already exists"; \
	fi
	@echo "✓ Setup complete!"

# Install Python dependencies
install:
	@echo "📦 Installing Python dependencies..."
	@pip install -r requirements.txt
	@echo "✓ Dependencies installed!"

# Start Docker services
start:
	@echo "🚀 Starting Docker services..."
	@docker-compose up -d
	@echo ""
	@echo "⏳ Waiting for services to be ready..."
	@sleep 5
	@echo ""
	@make status
	@echo ""
	@echo "✓ Services started successfully!"
	@echo ""
	@echo "Access URLs:"
	@echo "  • Grafana:    http://localhost:3000 (admin/admin)"
	@echo "  • HiveMQ:     http://localhost:8080"
	@echo "  • InfluxDB:   http://localhost:8086 (admin/adminpassword)"

# Stop Docker services
stop:
	@echo "🛑 Stopping Docker services..."
	@docker-compose stop
	@echo "✓ Services stopped!"

# Restart Docker services
restart:
	@echo "🔄 Restarting Docker services..."
	@docker-compose restart
	@echo "✓ Services restarted!"

# Show service status
status:
	@echo "📊 Service Status:"
	@docker-compose ps

# Show logs from all services
logs:
	@docker-compose logs -f

# Run publisher (foreground)
publisher:
	@echo "📡 Starting Publisher..."
	@cd publisher && python publisher.py

# Run subscriber (foreground)
subscriber:
	@echo "📩 Starting Subscriber..."
	@cd subscriber && python subscriber.py

# Run both in separate terminals (requires tmux or manual)
run:
	@echo "🚀 Starting Publisher and Subscriber..."
	@echo ""
	@echo "⚠️  Please run these commands in separate terminals:"
	@echo ""
	@echo "Terminal 1: make publisher"
	@echo "Terminal 2: make subscriber"
	@echo ""
	@echo "Or use: make run-bg (to run in background)"

# Run both in background
run-bg:
	@echo "🚀 Starting Publisher and Subscriber in background..."
	@cd publisher && nohup python publisher.py > publisher.log 2>&1 & echo $$! > publisher.pid
	@cd subscriber && nohup python subscriber.py > subscriber.log 2>&1 & echo $$! > subscriber.pid
	@sleep 2
	@echo "✓ Publisher started (PID: $$(cat publisher/publisher.pid))"
	@echo "✓ Subscriber started (PID: $$(cat subscriber/subscriber.pid))"
	@echo ""
	@echo "View logs:"
	@echo "  make logs-pub   # Publisher logs"
	@echo "  make logs-sub   # Subscriber logs"
	@echo ""
	@echo "Stop apps:"
	@echo "  make stop-apps"

# Stop background apps
stop-apps:
	@echo "🛑 Stopping Publisher and Subscriber..."
	@if [ -f publisher/publisher.pid ]; then \
		kill $$(cat publisher/publisher.pid) 2>/dev/null || true; \
		rm publisher/publisher.pid; \
		echo "✓ Publisher stopped"; \
	fi
	@if [ -f subscriber/subscriber.pid ]; then \
		kill $$(cat subscriber/subscriber.pid) 2>/dev/null || true; \
		rm subscriber/subscriber.pid; \
		echo "✓ Subscriber stopped"; \
	fi

# Show publisher logs
logs-pub:
	@if [ -f publisher/publisher.log ]; then \
		tail -f publisher/publisher.log; \
	else \
		echo "❌ No publisher log file found. Is it running?"; \
	fi

# Show subscriber logs
logs-sub:
	@if [ -f subscriber/subscriber.log ]; then \
		tail -f subscriber/subscriber.log; \
	else \
		echo "❌ No subscriber log file found. Is it running?"; \
	fi

# Open Grafana dashboard
dashboard:
	@echo "🌐 Opening Grafana dashboard..."
	@"$$BROWSER" http://localhost:3000 || xdg-open http://localhost:3000 || open http://localhost:3000 || echo "Please open http://localhost:3000 in your browser"

# Restart Grafana (useful if dashboard not loading)
restart-grafana:
	@echo "🔄 Restarting Grafana..."
	@docker-compose restart grafana
	@echo "⏳ Waiting for Grafana to initialize..."
	@sleep 10
	@echo "✓ Grafana restarted! Refresh your browser."

# Open HiveMQ Control Center
hivemq:
	@echo "🌐 Opening HiveMQ Control Center..."
	@"$$BROWSER" http://localhost:8080 || xdg-open http://localhost:8080 || open http://localhost:8080 || echo "Please open http://localhost:8080 in your browser"

# Open InfluxDB UI
influxdb:
	@echo "🌐 Opening InfluxDB UI..."
	@"$$BROWSER" http://localhost:8086 || xdg-open http://localhost:8086 || open http://localhost:8086 || echo "Please open http://localhost:8086 in your browser"

# Clean up (keep volumes)
clean:
	@echo "🧹 Cleaning up..."
	@make stop-apps 2>/dev/null || true
	@docker-compose down
	@rm -f publisher/publisher.log publisher/publisher.pid
	@rm -f subscriber/subscriber.log subscriber/subscriber.pid
	@echo "✓ Cleanup complete! (volumes preserved)"

# Clean everything including volumes
clean-all:
	@echo "⚠️  WARNING: This will delete all data including InfluxDB data!"
	@echo "Press Ctrl+C to cancel, or wait 5 seconds to continue..."
	@sleep 5
	@echo "🧹 Cleaning everything..."
	@make stop-apps 2>/dev/null || true
	@docker-compose down -v
	@rm -f publisher/publisher.log publisher/publisher.pid
	@rm -f subscriber/subscriber.log subscriber/subscriber.pid
	@echo "✓ Everything cleaned! (including volumes)"
