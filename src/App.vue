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
    </select>

    <button @click="uploadFile">Upload File</button>
    <br />
    <button @click="getTranscriptionResult" :disabled="!jobId">
      Get Transcription Result
    </button>
    <p>{{ transcriptionResult }}</p>
    <p v-if="errorMessage" style="color: red">{{ errorMessage }}</p>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "App",
  data() {
    return {
      selectedLanguage: "en-US",
      jobId: null,
      transcriptionResult: "",
      errorMessage: "",
      fileUrl: "", // เก็บ URL ของไฟล์หลังการอัปโหลด
    };
  },
  methods: {
    async getPresignedUrl() {
      try {
        const response = await axios.post(
          "https://kpf28u1ty3.execute-api.ap-southeast-2.amazonaws.com/dev/presigned-url"
        );
        if (response.data && response.data.pre_signed_url) {
          console.log("Presigned URL fetched:", response.data.pre_signed_url);
          return response.data;
        } else {
          throw new Error("Invalid response from presigned URL API");
        }
      } catch (error) {
        console.error("Error fetching presigned URL:", error);
        this.errorMessage =
          error.response?.data || "Error fetching presigned URL";
        return null;
      }
    },
    async handleFileUpload(event) {
      const file = event.target.files[0];
      if (file) {
        try {
          const presignedData = await this.getPresignedUrl();
          if (presignedData && presignedData.pre_signed_url) {
            this.fileUrl = presignedData.pre_signed_url.split("?")[0]; // Set URL ของไฟล์เพื่อใช้ในการ transcribe
            await this.uploadFile(file, presignedData);
          }
        } catch (error) {
          console.error("Error handling file upload:", error);
        }
      }
    },
    async uploadFile(file, presignedData) {
      try {
        console.log("Uploading file to S3 with URL:", this.fileUrl);

        const uploadResponse = await axios.put(
          presignedData.pre_signed_url,
          file,
          {
            headers: {
              "Content-Type": file.type || "audio/mpeg",
            },
          }
        );
        console.log("File uploaded successfully:", uploadResponse.status);
        await this.transcribeFile(); // เรียกใช้ฟังก์ชัน transcription หลังการอัปโหลดสำเร็จ
      } catch (error) {
        console.error("Error uploading file:", error);
        this.errorMessage = error.response?.data || "Error uploading file";
      }
    },
    async transcribeFile() {
      try {
        // ส่ง URL และ language code ไปยัง Lambda function ที่มีอยู่
        const response = await axios.post(
          "https://kpf28u1ty3.execute-api.ap-southeast-2.amazonaws.com/dev/transcription",
          {
            file_url: this.fileUrl, // ใช้ fileUrl จากการอัปโหลด
            language_code: this.selectedLanguage,
          }
        );
        this.jobId = response.data.job_id; // เก็บ job_id เพื่อใช้ในการดึงผลลัพธ์
        console.log("Transcription job started with job ID:", this.jobId);
      } catch (error) {
        console.error("Error starting transcription:", error);
        this.errorMessage =
          error.response?.data || "Error starting transcription";
      }
    },

    async getTranscriptionResult() {
      try {
        if (!this.jobId) {
          throw new Error("Job ID is required to fetch transcription result");
        }

        const response = await axios.get(
          "https://kpf28u1ty3.execute-api.ap-southeast-2.amazonaws.com/dev/transcription-result",
          {
            params: { job_id: this.jobId },
          }
        );

        // ตรวจสอบโครงสร้างของผลลัพธ์
        console.log("Transcription result:", response.data);

        // ตรวจสอบว่ามี 'results' และ 'transcripts'
        if (response.data.results && response.data.results.transcripts) {
          this.transcriptionResult =
            response.data.results.transcripts[0].transcript;
        } else {
          throw new Error("Transcription result is not available");
        }
      } catch (error) {
        console.error(
          "Error fetching transcription result:",
          error.response ? error.response.data : error.message
        );
        this.errorMessage =
          error.response?.data?.error || "Error fetching transcription result";
      }
    },
  },
};
</script>

<style scoped>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
