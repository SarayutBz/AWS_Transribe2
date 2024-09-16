<template>
  <div id="app">
    <h1>Upload MP3 and Transcribe</h1>
    <input type="file" @change="handleFileUpload" />

    <!-- Dropdown สำหรับเลือกภาษา -->
    <label for="language">Select Language:</label>
    <select v-model="selectedLanguage">
      <option value="en-US">English (US)</option>
      <option value="th-TH">Thai (Thailand)</option>
      <option value="zh-CN">Chinese (Mandarin)</option>
      <option value="ja-JP">Japanese</option>
      <option value="ko-KR">Korean</option>
      <!-- เพิ่มภาษาตามต้องการ -->
    </select>

    <button @click="uploadFile">Upload File</button>
    <br />
    <button @click="getTranscriptionResult" :disabled="!jobComplete">
      Get Transcription Result
    </button>
    <p>{{ transcriptionResult }}</p>
    <p v-if="errorMessage" style="color: red">{{ errorMessage }}</p>
  </div>
</template>
