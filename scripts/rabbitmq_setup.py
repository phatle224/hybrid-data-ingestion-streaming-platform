"""
RabbitMQ Setup Script for Affina CDC
Role: Data Engineer - Infrastructure setup
Pattern: CDC-based routing (insert/update/delete)
"""

import pika
import sys
import os

# Configuration from environment variables
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', '5672'))
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'admin')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'admin')
RABBITMQ_VHOST = os.getenv('RABBITMQ_VHOST', '/affina')

def setup_rabbitmq_infrastructure():
    """Setup exchanges, queues, and bindings for CDC events"""
    
    try:
        # Connect
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        parameters = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            virtual_host=RABBITMQ_VHOST,
            credentials=credentials,
            connection_attempts=3,
            retry_delay=2
        )
        
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        
        print("=" * 60)
        print("RABBITMQ INFRASTRUCTURE SETUP")
        print("=" * 60)
        
        # ===== 1. EXCHANGES =====
        print("\nCreating Exchanges...")
        
        exchanges = {
            'affina.cdc.events': 'topic',      # Main CDC events
            'affina.dlx': 'topic',              # Dead letter exchange
        }
        
        for exchange_name, exchange_type in exchanges.items():
            channel.exchange_declare(
                exchange=exchange_name,
                exchange_type=exchange_type,
                durable=True
            )
            print(f"   [OK] {exchange_name} (type: {exchange_type})")
        
        # ===== 2. QUEUES =====
        print("\nCreating Queues...")
        
        # Define queues for each application with their routing patterns
        queues = [
            # {
            #     'name': 'qc_app_queue',
            #     'description': 'QC Application - Quality Control',
            #     'routing_keys': [
            #         'claim.insert',
            #         'claim.update',
            #         'contract.insert',
            #         'contract.update'
            #     ]
            # },
            {
                'name': 'doc_ocr_queue',
                'description': 'Document OCR Application',
                'routing_keys': [
                    'claim.insert',
                    'claim.update',
                    'contract.insert',
                    'contract.update'
                ]
            }
            # {
            #     'name': 'recagent_queue',
            #     'description': 'Recommendation Agent',
            #     'routing_keys': [
            #         'claim.insert',
            #         'claim.update',
            #         'contract.insert',
            #         'contract.update',
            #         'profiling_analysis.insert',
            #         'profiling_analysis.update'
            #     ]
            # },
            # {
            #     'name': 'claim_app_queue',
            #     'description': 'Claim Application - Main claim processing',
            #     'routing_keys': [
            #         'claim.insert',
            #         'claim.update'
            #     ]
            # },
            # {
            #     'name': 'reporting_app_queue',
            #     'description': 'Reporting Application - Analytics & Reports',
            #     'routing_keys': [
            #         'claim.insert',
            #         'claim.update',
            #         'contract.insert',
            #         'contract.update',
            #         'profiling_analysis.insert',
            #         'profiling_analysis.update'
            #     ]
            # }
        ]
        
        for queue_config in queues:
            queue_name = queue_config['name']
            
            # Declare queue with DLX configuration
            channel.queue_declare(
                queue=queue_name,
                durable=True,
                arguments={
                    'x-dead-letter-exchange': 'affina.dlx',
                    'x-message-ttl': 86400000,  # 24 hours (1 day)
                    'x-max-length': 100000,     # Max 100k messages
                }
            )
            
            print(f"\n   ✅ {queue_name}")
            print(f"      {queue_config['description']}")
            print(f"      Routing Keys:")
            
            # Bind queue to exchange with routing keys
            for routing_key in queue_config['routing_keys']:
                channel.queue_bind(
                    exchange='affina.cdc.events',
                    queue=queue_name,
                    routing_key=routing_key
                )
                print(f"         - {routing_key}")
        
        # ===== 3. DEAD LETTER QUEUE =====
        print("\nCreating Dead Letter Queue...")
        
        channel.queue_declare(
            queue='dlx_queue',
            durable=True,
            arguments={
                'x-max-length': 10000,  # Max 10k failed messages
            }
        )
        channel.queue_bind(
            exchange='affina.dlx',
            queue='dlx_queue',
            routing_key='#'  # Catch all
        )
        print("   [OK] dlx_queue (catches all failed messages)")
        
        connection.close()
        
        # ===== SUMMARY =====
        print("\n" + "=" * 60)
        print("RABBITMQ SETUP COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"\nManagement UI: http://localhost:15672")
        print(f"   Username: {RABBITMQ_USER}")
        print(f"   Password: {RABBITMQ_PASS}")
        print(f"   VHost: {RABBITMQ_VHOST}")
        print("\nCreated:")
        print(f"   - 2 Exchanges")
        print(f"   - 1 Application Queue (doc_ocr_queue)")
        print(f"   - 1 Dead Letter Queue")
        print(f"\nNote: Other queues (qc_app_queue, claim_app_queue, recagent_queue, reporting_app_queue) are commented out")
        print("\nNext Step:")
        print("   Run: python rabbitmq_producer/event_publisher.py")
        print("=" * 60 + "\n")
        
        return True
        
    except pika.exceptions.AMQPConnectionError as e:
        print(f"\n[ERROR] Connection Error: {e}")
        print("\nTips:")
        print("   1. Check if RabbitMQ is running:")
        print("      docker ps | grep rabbitmq")
        print("   2. Start RabbitMQ:")
        print("      docker-compose -f docker-compose.rabbitmq.yml up -d")
        print("   3. Wait 10 seconds and try again")
        return False
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return False

if __name__ == '__main__':
    success = setup_rabbitmq_infrastructure()
    sys.exit(0 if success else 1)
