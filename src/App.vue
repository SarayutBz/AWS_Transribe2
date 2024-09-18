<template>
  <div id="app" class="container mx-auto p-8 bg-white rounded-lg shadow-md">
    <!-- หัวข้อหลัก -->
    <h1 class="text-4xl font-bold text-center text-blue-600 mb-8">
      Upload or Record Audio
    </h1>

    <!-- การอัปโหลดไฟล์ -->
    <div class="mb-6">
      <label class="block text-lg font-medium text-gray-700 mb-3">
        Upload MP3 File:
      </label>
      <input
        type="file"
        @change="handleFileUpload"
        class="block w-full text-gray-600 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-600 hover:file:bg-blue-100"
      />
    </div>

    <!-- เลือกภาษา -->
    <div class="mb-6">
      <label class="block text-lg font-medium text-gray-700 mb-3">
        Select Language:
      </label>
      <select
        v-model="selectedLanguage"
        class="block w-full px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
      >
        <option value="en-US">English (US)</option>
        <option value="th-TH">Thai (Thailand)</option>
        <option value="zh-CN">Chinese (Mandarin)</option>
        <option value="ja-JP">Japanese</option>
        <option value="ko-KR">Korean</option>
      </select>
    </div>

    <!-- ปุ่มอัปโหลด -->
    <div class="text-center mb-6">
      <button
        @click="uploadFileToS3"
        :disabled="isUploading || !file"
        class="px-6 py-3 bg-blue-600 text-white font-semibold rounded-full shadow hover:bg-blue-700 disabled:opacity-50 transition-all duration-300 ease-in-out"
      >
        Upload File
      </button>
    </div>

    <!-- โหลดไฟล์ -->
    <div v-if="isUploading" class="text-center mb-6">
      <div class="loader"></div>
      <p class="text-gray-500">Uploading file... Please wait.</p>
    </div>

    <!-- อัดเสียง -->
    <div class="flex justify-center mb-6 space-x-4">
      <button
        @click="startRecording"
        :disabled="isRecording"
        class="px-6 py-3 bg-green-600 text-white font-semibold rounded-full shadow hover:bg-green-700 disabled:opacity-50 transition-all duration-300 ease-in-out"
      >
        Start Recording
      </button>
      <button
        @click="stopRecording"
        :disabled="!isRecording"
        class="px-6 py-3 bg-red-600 text-white font-semibold rounded-full shadow hover:bg-red-700 disabled:opacity-50 transition-all duration-300 ease-in-out"
      >
        Stop Recording
      </button>
    </div>

    <!-- ปุ่มเริ่มถอดความ -->
    <div class="text-center mb-6">
      <button
        @click="transcribeFile"
        :disabled="!fileUrl || isTranscribing"
        class="px-6 py-3 bg-purple-600 text-white font-semibold rounded-full shadow hover:bg-purple-700 disabled:opacity-50 transition-all duration-300 ease-in-out"
      >
        Start Transcription
      </button>
    </div>

    <!-- โหลดถอดความ -->
    <div v-if="isTranscribing" class="text-center mb-6">
      <div class="loader"></div>
      <p class="text-gray-500">Transcribing... Please wait.</p>
    </div>

    <!-- ปุ่มดึงผลลัพธ์ -->
    <div class="text-center mb-6">
      <button
        @click="getTranscriptionResult"
        :disabled="!jobId || isFetchingResult"
        class="px-6 py-3 bg-yellow-600 text-white font-semibold rounded-full shadow hover:bg-yellow-700 disabled:opacity-50 transition-all duration-300 ease-in-out"
      >
        Get Transcription Result
      </button>
    </div>

    <!-- ปุ่มสำหรับดาวน์โหลด PDF -->
    <div class="mb-6 text-center">
      <button
        @click="exportPDF"
        :disabled="!transcriptionResult"
        class="px-4 py-2 bg-indigo-600 text-white font-semibold rounded-md shadow hover:bg-indigo-700 disabled:opacity-50"
      >
        Download PDF
      </button>
    </div>

    <!-- โหลดผลลัพธ์ -->
    <div v-if="isFetchingResult" class="text-center mb-6">
      <div class="loader"></div>
      <p class="text-gray-500">Fetching transcription result... Please wait.</p>
    </div>

    <!-- สถานะ -->
    <div
      v-if="statusMessage"
      class="bg-gray-100 p-4 rounded-lg shadow-md text-center mb-6"
    >
      <p class="text-gray-600">{{ statusMessage }}</p>
    </div>

    <!-- ผลลัพธ์การถอดความ -->
    <div
      v-if="transcriptionResult"
      class="bg-gray-100 p-6 rounded-lg shadow-md"
    >
      <h2 class="text-lg font-bold text-gray-700 mb-3">
        Transcription Result:
      </h2>
      <p class="text-gray-600">{{ transcriptionResult }}</p>
    </div>

    <!-- ข้อความแสดงข้อผิดพลาด -->
    <p v-if="errorMessage" class="text-red-600 text-center mt-6">
      {{ errorMessage }}
    </p>
  </div>
</template>

<script>
import axios from "axios";
import jsPDF from "jspdf";


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
      isRecording: false,
      mediaRecorder: null,
      audioChunks: [],
      file: null,
      statusMessage: "",
    };
  },
  methods: {
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
        this.errorMessage = error.response?.data || "Error during file upload";
        console.error("Error during file upload:", error);
      } finally {
        this.isUploading = false;
      }
    },

    async getPresignedUrl() {
      try {
        const response = await axios.post(
          "https://kpf28u1ty3.execute-api.ap-southeast-2.amazonaws.com/dev/presigned-url"
        );
        return response.data?.pre_signed_url ?? null;
      } catch (error) {
        this.errorMessage =
          error.response?.data || "Error fetching presigned URL";
        console.error("Error fetching presigned URL:", error);
        return null;
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
        console.error("Error uploading file:", error);
      }
    },

    async transcribeFile() {
      if (!this.fileUrl) return;

      this.isTranscribing = true;
      this.statusMessage = "Transcribing... Please wait.";
      try {
        const response = await axios.post(
          "https://kpf28u1ty3.execute-api.ap-southeast-2.amazonaws.com/dev/transcription",
          {
            file_url: this.fileUrl,
            language_code: this.selectedLanguage,
          }
        );
        this.jobId = response.data.job_id;
        await this.checkTranscriptionStatus();
      } catch (error) {
        this.errorMessage =
          error.response?.data || "Error starting transcription";
        console.error("Error starting transcription:", error);
      } finally {
        this.isTranscribing = false;
        this.statusMessage = "";
      }
    },

    async checkTranscriptionStatus() {
      if (!this.jobId) return;

      try {
        let isJobComplete = false;
        while (!isJobComplete) {
          const response = await axios.get(
            "https://kpf28u1ty3.execute-api.ap-southeast-2.amazonaws.com/dev/transcription-status",
            { params: { job_id: this.jobId } }
          );

          const status = response.data.status;
          if (status === "COMPLETED") {
            isJobComplete = true;
          } else if (status === "FAILED") {
            throw new Error("Transcription job failed");
          }

          await new Promise((resolve) => setTimeout(resolve, 5000)); // Wait for 5 seconds before checking again
        }

        this.getTranscriptionResult();
      } catch (error) {
        this.errorMessage =
          error.response?.data || "Error checking transcription status";
        console.error("Error checking transcription status:", error);
      }
    },

    async getTranscriptionResult() {
      if (!this.jobId) return;

      this.isFetchingResult = true;
      try {
        const response = await axios.get(
          "https://kpf28u1ty3.execute-api.ap-southeast-2.amazonaws.com/dev/transcription-result",
          { params: { job_id: this.jobId } }
        );
        this.transcriptionResult =
          response.data.results.transcripts[0].transcript;
      } catch (error) {
        this.errorMessage =
          error.response?.data || "Error fetching transcription result";
        console.error("Error fetching transcription result:", error);
      } finally {
        this.isFetchingResult = false;
      }
    },

    startRecording() {
      navigator.mediaDevices
        .getUserMedia({ audio: true })
        .then((stream) => {
          this.mediaRecorder = new MediaRecorder(stream);
          this.mediaRecorder.ondataavailable = (event) => {
            this.audioChunks.push(event.data);
          };
          this.mediaRecorder.onstop = this.handleStopRecording.bind(this);
          this.mediaRecorder.start();
          this.isRecording = true;
        })
        .catch((error) => {
          this.errorMessage =
            error.message || "Error accessing microphone for recording";
          console.error("Error accessing microphone:", error);
        });
    },

    stopRecording() {
      if (this.mediaRecorder && this.isRecording) {
        this.mediaRecorder.stop();
      }
    },

    handleStopRecording() {
      const audioBlob = new Blob(this.audioChunks, { type: "audio/mpeg" });
      this.file = new File([audioBlob], "recording.mp3", {
        type: "audio/mpeg",
      });
      this.audioChunks = [];
      this.isRecording = false;
    },

    clearState() {
      this.file = null;
      this.fileUrl = "";
      this.jobId = null;
      this.transcriptionResult = "";
      this.errorMessage = "";
      this.statusMessage = "";
      this.isUploading = false;
      this.isTranscribing = false;
      this.isFetchingResult = false;
      this.isRecording = false;
    },
    // ฟังก์ชันสำหรับสร้างและดาวน์โหลด PDF
    exportPDF() {
      if (!this.transcriptionResult) return;

      const doc = new jsPDF(); // สร้างอินสแตนซ์ jsPDF
      const splitText = doc.splitTextToSize(this.transcriptionResult, 180); // แยกข้อความยาว
      doc.text(splitText, 10, 10); // เพิ่มข้อความลงใน PDF
      doc.save("transcription.pdf"); // ดาวน์โหลดไฟล์ PDF
    },
  },
};
</script>

<style scoped>
.loader {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-left-color: #3498db;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  animation: spin 1s linear infinite;
  margin: 0 auto 10px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
