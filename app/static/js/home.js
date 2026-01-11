/**
 * Home page JavaScript functionality
 * Handles toast notifications, tabs, parcel management, and PubNub integration
 */

// ==========================================
// Toast Notification System
// ==========================================

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer')
    const toast = document.createElement('div')
    toast.className = 'transform transition-all duration-300 ease-in-out translate-x-full opacity-0'

    const bgColors = {
        success: 'bg-gradient-to-r from-green-500 to-emerald-600',
        error: 'bg-gradient-to-r from-red-500 to-rose-600',
        info: 'bg-gradient-to-r from-blue-500 to-indigo-600'
    }

    const icons = {
        success: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>',
        error: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/></svg>',
        info: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/></svg>'
    }

    toast.innerHTML = `
        <div class="${bgColors[type] || bgColors.info} text-white px-4 sm:px-6 py-3 sm:py-4 rounded-xl shadow-2xl flex items-center gap-2 sm:gap-3 w-full sm:min-w-[320px]">
            <div class="flex-shrink-0">${icons[type] || icons.info}</div>
            <p class="flex-1 font-medium text-xs sm:text-sm">${message}</p>
            <button onclick="this.parentElement.parentElement.remove()" class="flex-shrink-0 hover:bg-white/20 rounded-lg p-1 transition">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>
            </button>
        </div>
    `

    toastContainer.appendChild(toast)

    // Animate in
    setTimeout(() => {
        toast.classList.remove('translate-x-full', 'opacity-0')
    }, 10)

    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.classList.add('translate-x-full', 'opacity-0')
        setTimeout(() => toast.remove(), 300)
    }, 5000)
}

// ==========================================
// Tab Navigation
// ==========================================

let currentTab = 'active'

function switchTab(tab) {
    currentTab = tab

    // Update tab buttons
    const activeTabBtn = document.getElementById('activeTab')
    const historyTabBtn = document.getElementById('historyTab')

    if (tab === 'active') {
        activeTabBtn.className = 'flex-1 px-3 sm:px-6 py-2.5 sm:py-3 font-semibold rounded-lg sm:rounded-xl bg-white text-indigo-600 shadow-md transition duration-200 text-sm sm:text-base'
        historyTabBtn.className = 'flex-1 px-3 sm:px-6 py-2.5 sm:py-3 font-semibold rounded-lg sm:rounded-xl text-gray-600 hover:bg-white/50 transition duration-200 text-sm sm:text-base'
        document.getElementById('activeContent').classList.remove('hidden')
        document.getElementById('historyContent').classList.add('hidden')
    } else {
        historyTabBtn.className = 'flex-1 px-3 sm:px-6 py-2.5 sm:py-3 font-semibold rounded-lg sm:rounded-xl bg-white text-indigo-600 shadow-md transition duration-200 text-sm sm:text-base'
        activeTabBtn.className = 'flex-1 px-3 sm:px-6 py-2.5 sm:py-3 font-semibold rounded-lg sm:rounded-xl text-gray-600 hover:bg-white/50 transition duration-200 text-sm sm:text-base'
        document.getElementById('historyContent').classList.remove('hidden')
        document.getElementById('activeContent').classList.add('hidden')
    }

    // Clear messages
    document.getElementById('parcelsMessage').innerHTML = ''
}

// ==========================================
// Parcel Fetching
// ==========================================

async function fetchActiveParcels() {
    try {
        const response = await fetch('/api/fetch-parcels?status=active')
        const data = await response.json()

        if (data.type === 'error') {
            showMessage('parcelsMessage', data)
            document.getElementById('activeParcels').innerHTML = ''
            return
        }

        document.getElementById('parcelsMessage').innerHTML = ''
        const activeParcels = document.getElementById('activeParcels')

        if (data.parcels && data.parcels.length > 0) {
            activeParcels.innerHTML = data.parcels.map(parcel => `
                <div class="border-2 border-gray-200 rounded-xl sm:rounded-2xl p-4 sm:p-8 mb-4 sm:mb-5 hover:shadow-2xl hover:border-indigo-300 transition-all duration-300 bg-gradient-to-br from-white to-gray-50">
                    <div class="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-3 sm:gap-0 mb-4 sm:mb-5">
                        <div class="flex-1">
                            <h3 class="text-lg sm:text-2xl font-bold text-gray-800 mb-1 sm:mb-2">${parcel.parcel_name}</h3>
                            <p class="text-xs sm:text-sm text-gray-500 mb-1">🏷️ Parcel ID: <span class="font-mono font-semibold">${parcel.id}</span></p>
                            ${parcel.is_delivered ? `<p class="text-xs sm:text-sm text-gray-500">📅 Delivered: ${new Date(parcel.delivered_at).toLocaleString()}</p>` : ''}
                        </div>
                        <span class="self-start px-3 sm:px-4 py-1.5 sm:py-2 rounded-full text-xs sm:text-sm font-bold shadow-md ${parcel.is_delivered ? 'bg-gradient-to-r from-green-400 to-emerald-500 text-white' : 'bg-gradient-to-r from-yellow-400 to-orange-500 text-white'}">
                            ${parcel.is_delivered ? '✓ Ready' : '⏳ In Transit'}
                        </span>
                    </div>
                    
                    <div class="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg sm:rounded-xl p-3 sm:p-5 mb-4 sm:mb-5 border border-indigo-100">
                        <p class="text-xs font-semibold text-indigo-600 uppercase tracking-wide mb-1 sm:mb-2">📍 Collection Point</p>
                        <p class="text-base sm:text-lg font-bold text-indigo-700">Box: ${parcel.box_name}</p>
                        <p class="text-xs sm:text-sm text-gray-600">${parcel.location}</p>
                    </div>

                    ${parcel.is_delivered ? `
                    <div class="bg-gradient-to-r from-yellow-50 to-amber-50 border-l-4 border-yellow-400 p-3 sm:p-5 mb-4 sm:mb-5 rounded-lg shadow-sm">
                        <div class="flex gap-2 sm:gap-3">
                            <div class="flex-shrink-0">
                                <svg class="h-5 w-5 sm:h-6 sm:w-6 text-yellow-500" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                                </svg>
                            </div>
                            <div>
                                <p class="text-xs sm:text-sm font-semibold text-yellow-800 mb-1">⚠️ Important Notice</p>
                                <p class="text-xs sm:text-sm text-yellow-700">
                                    Only click "Unlock Box" when you are <span class="font-bold">physically at the collection point</span> and ready to collect your parcel immediately.
                                </p>
                            </div>
                        </div>
                    </div>
                    <div id="buttons-${parcel.id}">
                        <button 
                            onclick="unlockBox('${parcel.id}', '${parcel.box_id}')"
                            class="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-bold py-3 sm:py-4 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-1 flex items-center justify-center gap-2 sm:gap-3 text-sm sm:text-base"
                        >
                            <svg class="w-5 h-5 sm:w-6 sm:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z"/>
                            </svg>
                            <span>Unlock Box</span>
                        </button>
                    </div>
                    ` : '<div class="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg sm:rounded-xl p-4 sm:p-5 text-center"><p class="text-gray-500 text-xs sm:text-sm font-medium">📦 Parcel is still in transit to collection point</p></div>'}
                </div>
            `).join('')
        } else {
            activeParcels.innerHTML = `
                <div class="text-center py-10 sm:py-16 bg-gradient-to-br from-gray-50 to-indigo-50 rounded-xl sm:rounded-2xl border-2 border-dashed border-gray-300">
                    <div class="inline-flex items-center justify-center w-16 h-16 sm:w-20 sm:h-20 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-full mb-3 sm:mb-4">
                        <svg class="w-8 h-8 sm:w-10 sm:h-10 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>
                        </svg>
                    </div>
                    <p class="text-gray-500 font-semibold text-base sm:text-lg">No active parcels</p>
                    <p class="text-gray-400 text-xs sm:text-sm mt-2">Register a parcel above to get started</p>
                </div>
            `
        }
    } catch (e) {
        showMessage('parcelsMessage', {
            error: 'Connection error. Please refresh.',
            type: 'error'
        })
        document.getElementById('activeParcels').innerHTML = ''
    }
}

async function fetchHistoryParcels() {
    try {
        const response = await fetch('/api/fetch-parcels?status=history')
        const data = await response.json()

        if (data.type === 'error') {
            showMessage('parcelsMessage', data)
            document.getElementById('historyParcels').innerHTML = ''
            return
        }

        document.getElementById('parcelsMessage').innerHTML = ''
        const historyParcels = document.getElementById('historyParcels')

        if (data.parcels && data.parcels.length > 0) {
            historyParcels.innerHTML = data.parcels.map(parcel => `
                <div class="border-2 border-gray-200 rounded-2xl p-7 mb-4 bg-gradient-to-br from-gray-50 to-gray-100 hover:shadow-lg transition-all duration-300">
                    <div class="flex justify-between items-start mb-4">
                        <div class="flex-1">
                            <h3 class="text-xl font-bold text-gray-800 mb-2">${parcel.parcel_name}</h3>
                            <p class="text-sm text-gray-500 font-mono">🏷️ ID: ${parcel.id}</p>
                        </div>
                        <span class="px-4 py-2 rounded-full text-sm font-bold bg-gradient-to-r from-gray-400 to-gray-500 text-white shadow-md">
                            ✓ Collected
                        </span>
                    </div>
                    
                    <div class="bg-white rounded-xl p-4 space-y-2 border border-gray-200">
                        <div class="flex items-center gap-2 text-gray-700">
                            <svg class="w-5 h-5 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
                            </svg>
                            <span class="font-semibold text-sm">Box: ${parcel.box_name}</span>
                            <span class="text-gray-400">•</span>
                            <span class="text-sm">${parcel.location}</span>
                        </div>
                        <div class="flex items-center gap-2 text-gray-700">
                            <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                            <span class="text-sm font-medium">${new Date(parcel.collected_at).toLocaleString()}</span>
                        </div>
                    </div>
                </div>
            `).join('')
        } else {
            historyParcels.innerHTML = `
                <div class="text-center py-16 bg-gradient-to-br from-gray-50 to-slate-100 rounded-2xl border-2 border-dashed border-gray-300">
                    <div class="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-gray-100 to-slate-200 rounded-full mb-4">
                        <svg class="w-10 h-10 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                    </div>
                    <p class="text-gray-500 font-semibold text-lg">No collection history yet</p>
                    <p class="text-gray-400 text-sm mt-2">Your collected parcels will appear here</p>
                </div>
            `
        }
    } catch (e) {
        showMessage('parcelsMessage', {
            error: 'Connection error. Please refresh.',
            type: 'error'
        })
        document.getElementById('historyParcels').innerHTML = ''
    }
}

// ==========================================
// Box Control Functions
// ==========================================

async function unlockBox(parcelId, boxId) {
    try {
        const response = await fetch("/api/open-box", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ parcel_id: parcelId })
        })

        const data = await response.json()
        if (data.message) showToast(data.message, data.type)
        else if (data.error) showToast(data.error, data.type)

        if (data.type === 'success') {
            // Replace unlock button with lock and collected buttons
            const buttonsContainer = document.getElementById(`buttons-${parcelId}`)
            if (buttonsContainer) {
                buttonsContainer.innerHTML = `
                    <div class="grid grid-cols-2 gap-3">
                        <button 
                            onclick="lockBox('${parcelId}', '${boxId}')"
                            class="bg-gradient-to-r from-gray-600 to-gray-700 hover:from-gray-700 hover:to-gray-800 text-white font-bold py-4 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-1 flex items-center justify-center gap-2"
                        >
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                            </svg>
                            <span>Lock Box</span>
                        </button>
                        <button 
                            onclick="markCollected('${parcelId}')"
                            class="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-bold py-4 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-1 flex items-center justify-center gap-2"
                        >
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                            </svg>
                            <span>Collected</span>
                        </button>
                    </div>
                `
            }
        }
    } catch (e) {
        showToast('Connection error. Please try again.', 'error')
    }
}

async function lockBox(parcelId, boxId) {
    try {
        const response = await fetch('/api/lock-box', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ box_id: boxId })
        })

        const data = await response.json()
        if (data.message) showToast(data.message, data.type)
        else if (data.error) showToast(data.error, data.type)

        if (data.type === 'success') {
            // Replace lock/collected buttons with unlock button
            const buttonsContainer = document.getElementById(`buttons-${parcelId}`)
            if (buttonsContainer) {
                buttonsContainer.innerHTML = `
                    <button 
                        onclick="unlockBox('${parcelId}', '${boxId}')"
                        class="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-bold py-4 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-1 flex items-center justify-center gap-3"
                    >
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z"/>
                        </svg>
                        <span>Unlock Box</span>
                    </button>
                `
            }
        }
    } catch (e) {
        showToast('Connection error. Please try again.', 'error')
    }
}

// ==========================================
// Weight Warning Modal & Collection
// ==========================================

let pendingCollectionParcelId = null

function showWeightWarningModal(parcelId) {
    pendingCollectionParcelId = parcelId
    document.getElementById('weightWarningModal').classList.remove('hidden')
}

function closeWeightWarningModal() {
    pendingCollectionParcelId = null
    document.getElementById('weightWarningModal').classList.add('hidden')
}

async function forceMarkCollected() {
    if (!pendingCollectionParcelId) return

    try {
        const response = await fetch('/api/mark-collected', {
            method: "POST",
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                parcel_id: pendingCollectionParcelId,
                force: true  // Force collection despite weight
            })
        })

        const data = await response.json()
        closeWeightWarningModal()

        if (data.message) showToast(data.message, data.type)
        else if (data.error) showToast(data.error, data.type)

        if (data.type === 'success') {
            // Fade out the parcel card before removing
            const parcelCard = document.querySelector(`#buttons-${pendingCollectionParcelId}`)?.closest('.border-2')
            if (parcelCard) {
                parcelCard.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out'
                parcelCard.style.opacity = '0'
                parcelCard.style.transform = 'scale(0.95)'
                
                // Wait for animation then refresh
                setTimeout(() => {
                    fetchActiveParcels()
                    fetchHistoryParcels()
                }, 500)
            } else {
                // Fallback if card not found
                fetchActiveParcels()
                fetchHistoryParcels()
            }
        }
    } catch (e) {
        showToast('Connection error. Please try again.', 'error')
    }
}

async function markCollected(parcelId) {
    try {
        showToast('Checking if parcel was removed...', 'info')

        const response = await fetch('/api/mark-collected', {
            method: "POST",
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ parcel_id: parcelId })
        })

        const data = await response.json()

        if (data.type === 'weight_check') {
            // Wait for weight check response from load cell via PubNub
            // The response will be handled by PubNub listener
            // Store parcelId for later use
            window.pendingWeightCheckParcelId = parcelId
        } else if (data.type === 'success') {
            if (data.message) showToast(data.message, data.type)
            // Refresh parcels list
            fetchActiveParcels()
            fetchHistoryParcels()
        } else if (data.error) {
            showToast(data.error, data.type)
        }
    } catch (e) {
        showToast('Connection error. Please try again.', 'error')
    }
}

// ==========================================
// Form Registration Handler
// ==========================================

function initRegisterForm() {
    document.getElementById('registerParcelForm').addEventListener('submit', async (e) => {
        e.preventDefault()
        const parcelId = document.getElementById('parcelId').value

        try {
            const response = await fetch('/api/register-parcel', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ parcel_id: parcelId })
            })

            const data = await response.json()
            showMessage('registerMessage', data)

            if (data.type === 'success' || data.type === 'info') {
                document.getElementById('parcelId').value = ''
                fetchActiveParcels()
            }
        } catch (e) {
            showMessage('registerMessage', {
                error: 'Connection error. Please try again.',
                type: 'error'
            })
        }
    })
}

// ==========================================
// PubNub Initialization
// ==========================================

function initHomePubNub(userId, subscribeKey, pubnubToken) {
    initPubNub(userId, subscribeKey, pubnubToken, {
        onParcelDelivered: function (parcelInfo) {
            // Show notification when parcel is delivered
            showMessage('parcelsMessage', {
                message: `📦 Your parcel "${parcelInfo.parcel_name}" has been delivered to ${parcelInfo.box_name}!`,
                type: 'success'
            })

            // Refresh parcel list if on active tab
            if (currentTab === 'active') {
                fetchActiveParcels()
            }
        }
    })
}

// ==========================================
// Page Initialization
// ==========================================

function initHomePage(userId, subscribeKey, pubnubToken) {
    // Initialize form handler
    initRegisterForm()
    
    // Load parcels on page load
    fetchActiveParcels()
    fetchHistoryParcels()
    
    // Initialize PubNub for real-time notifications
    initHomePubNub(userId, subscribeKey, pubnubToken)
}
