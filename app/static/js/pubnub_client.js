/**
 * PubNub Client Initialization and Message Handling
 * Handles real-time notifications for parcel deliveries
 */

let pubnub = null

function initPubNub(userId, subscribeKey, onParcelDelivered) {
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
            handlePubNubMessage(event, onParcelDelivered)
        }
    })
}


function handlePubNubMessage(event, onParcelDelivered) {
    console.log('PubNub message received:', event)

    if (event.message.type === 'parcel_delivered') {
        // Trigger the callback with parcel information
        if (onParcelDelivered && typeof onParcelDelivered === 'function') {
            onParcelDelivered({
                parcel_name: event.message.parcel_name,
                box_name: event.message.box_name
            })
        }
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
