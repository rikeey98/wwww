<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
    <div class="max-w-4xl mx-auto">
      <h1 class="text-4xl font-bold text-gray-900 mb-8 text-center">
        Vue 3 + Tailwind CSS v4.1 테스트
      </h1>
      
      <!-- 버튼 테스트 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <button class="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg transition-colors">
          기본 버튼
        </button>
        
        <!-- v4.1 새 기능: 텍스트 섀도우 -->
        <button class="bg-purple-500 hover:bg-purple-600 text-white px-6 py-3 rounded-lg text-shadow-lg">
          텍스트 섀도우 버튼
        </button>
        
        <!-- 반응형 테스트 -->
        <div class="bg-white p-4 rounded-lg shadow-lg">
          <h3 class="text-lg font-semibold mb-2">반응형 테스트</h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <div class="bg-green-100 p-2 rounded">박스 1</div>
            <div class="bg-red-100 p-2 rounded">박스 2</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
