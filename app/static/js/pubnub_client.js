/**
 * PubNub Client Initialization and Message Handling
 * Handles real-time notifications for parcel deliveries
 */

let pubnub = null

function initPubNub(userId, subscribeKey, callbacks) {
    if (!subscribeKey || subscribeKey === 'None') {
        console.warn('PubNub subscribe key not configured')
        return
    }

    pubnub = new PubNub({
        subscribeKey: subscribeKey,
        uuid: `user-web-${userId}`
    })

    // Subscribe to user's notification channel
    pubnub.subscribe({
        channels: [`user-${userId}`]
    })

    // Add connection status listener
    pubnub.addListener({
        status: function (statusEvent) {
            if (statusEvent.category === "PNConnectedCategory") {
                console.log("✅ PubNub connected successfully")
            }
        },
        message: function (event) {
            console.log("📨 PubNub message received:", event.message)
            handlePubNubMessage(event, callbacks)
        }
    })
}


function handlePubNubMessage(event, callbacks) {
    console.log('📨 PubNub message received:', event.message)
    
    const messageType = event.message.type
    
    if (messageType === 'parcel_delivered' && callbacks.onParcelDelivered) {
        callbacks.onParcelDelivered(event.message)
    }
}

/**
 * Disconnect from PubNub
 */
function disconnectPubNub() {
    if (pubnub) {
        pubnub.unsubscribeAll()
        console.log("🔌 PubNub disconnected")
    }
}
