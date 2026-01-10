/**
 * PubNub Client Initialization and Message Handling
 * Handles real-time notifications for parcel deliveries and weight checks
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
    } else if (messageType === 'weight_check_response') {
        // Handle weight check response from load cell
        const hasWeight = event.message.has_weight
        const parcelId = event.message.parcel_id
        
        console.log(`⚖️ Weight check response for ${parcelId}: ${hasWeight ? 'HAS WEIGHT' : 'EMPTY'}`)
        
        if (hasWeight) {
            // Show warning modal
            console.log('⚠️ Weight detected, showing warning modal')
            if (typeof showWeightWarningModal === 'function') {
                showWeightWarningModal(parcelId)
            }
        } else {
            // No weight detected, directly mark as collected
            console.log('✅ No weight detected, marking as collected automatically')
            markAsCollectedAfterWeightCheck(parcelId)
        }
    }
}

/**
 * Mark parcel as collected after successful weight check
 */
async function markAsCollectedAfterWeightCheck(parcelId) {
    try {
        console.log(`🔄 Attempting to mark parcel ${parcelId} as collected...`)
        
        const response = await fetch('/api/mark-collected', {
            method: "POST",
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                parcel_id: parcelId,
                force: true  // Force collection since weight check passed
            })
        })

        const data = await response.json()
        
        if (data.message) {
            if (typeof showToast === 'function') {
                showToast(data.message, data.type)
            }
        } else if (data.error) {
            if (typeof showToast === 'function') {
                showToast(data.error, data.type)
            }
        }

        if (data.type === 'success') {
            console.log('✅ Parcel marked as collected successfully')
            // Refresh parcels list
            if (typeof fetchActiveParcels === 'function') {
                fetchActiveParcels()
            }
            if (typeof fetchHistoryParcels === 'function') {
                fetchHistoryParcels()
            }
        }
    } catch (e) {
        console.error('❌ Error marking parcel as collected:', e)
        if (typeof showToast === 'function') {
            showToast('Connection error. Please try again.', 'error')
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