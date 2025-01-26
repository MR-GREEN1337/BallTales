import React from 'react'

function loading() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-14 w-14 border-t-2 border-b-2 border-green-500"></div>
    </div>
  )
}

export default loading