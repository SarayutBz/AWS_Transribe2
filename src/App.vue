<template>
  <div id="app">
    <h1>Upload MP3 and Transcribe</h1>
    <input type="file" @change="handleFileUpload" />

    <label for="language">Select Language:</label>
    <select v-model="selectedLanguage">
      <option value="en-US">English (US)</option>
      <option value="th-TH">Thai (Thailand)</option>
      <option value="zh-CN">Chinese (Mandarin)</option>
      <option value="ja-JP">Japanese</option>
      <option value="ko-KR">Korean</option>
    </select>

    <!-- ปุ่มสำหรับอัปโหลดไฟล์ -->
    <button @click="uploadFileToS3" :disabled="isUploading || !file">
      Upload File
    </button>

    <!-- ปุ่มสำหรับเริ่มการถอดความหลังจากไฟล์ถูกอัปโหลด -->
    <button @click="transcribeFile" :disabled="!fileUrl || isTranscribing">
      Start Transcription
    </button>

    <button
      @click="getTranscriptionResult"
      :disabled="!jobId || isFetchingResult"
    >
      Get Transcription Result
    </button>

    <p v-if="transcriptionResult">{{ transcriptionResult }}</p>
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
      fileUrl: "",
      isUploading: false,
      isTranscribing: false,
      isFetchingResult: false,
      file: null, // เก็บไฟล์ที่เลือก
    };
  },
  methods: {
    async getPresignedUrl() {
      try {
        const response = await axios.post(
          "https://kpf28u1ty3.execute-api.ap-southeast-2.amazonaws.com/dev/presigned-url"
        );
        return response.data?.pre_signed_url ?? null;
      } catch (error) {
        this.errorMessage =
          error.response?.data || "Error fetching presigned URL";
        return null;
      }
    },

    handleFileUpload(event) {
      this.file = event.target.files[0];
    },

    async uploadFileToS3() {
      if (!this.file) return;

      this.isUploading = true;
      try {
        const presignedUrl = await this.getPresignedUrl();
        if (presignedUrl) {
          this.fileUrl = presignedUrl.split("?")[0];
          await this.uploadFile(this.file, presignedUrl);
        }
      } catch (error) {
        this.errorMessage = error.message;
      } finally {
        this.isUploading = false;
      }
    },

    async uploadFile(file, presignedUrl) {
      try {
        await axios.put(presignedUrl, file, {
          headers: {
            "Content-Type": file.type || "audio/mpeg",
          },
        });
      } catch (error) {
        this.errorMessage = error.response?.data || "Error uploading file";
      }
    },

    async transcribeFile() {
      if (!this.fileUrl) return;

      this.isTranscribing = true;
      try {
        const response = await axios.post(
          "https://kpf28u1ty3.execute-api.ap-southeast-2.amazonaws.com/dev/transcription",
          {
            file_url: this.fileUrl,
            language_code: this.selectedLanguage,
          }
        );
        this.jobId = response.data.job_id;
      } catch (error) {
        this.errorMessage =
          error.response?.data || "Error starting transcription";
      } finally {
        this.isTranscribing = false;
      }
    },

    async getTranscriptionResult() {
      if (!this.jobId) return;

      this.isFetchingResult = true;
      try {
        const response = await axios.get(
          "https://kpf28u1ty3.execute-api.ap-southeast-2.amazonaws.com/dev/transcription-result",
          {
            params: { job_id: this.jobId },
          }
        );

        if (response.data.results?.transcripts) {
          this.transcriptionResult = response.data.results.transcripts
            .map((transcript) => transcript.transcript)
            .join(" ");
        } else {
          throw new Error("Transcription result is not available");
        }
      } catch (error) {
        this.errorMessage =
          error.response?.data?.error || "Error fetching transcription result";
      } finally {
        this.isFetchingResult = false;
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
button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>
