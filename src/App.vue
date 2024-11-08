<template>

  <div class="min-h-screen bg-gray-100 py-12 px-6 lg:px-8">
    <div class="max-w-7xl mx-auto bg-white rounded-lg shadow-lg p-10">
      <!-- Header -->
      <div class="flex flex-col justify-center items-center text-center m-5">
        <img
          src="@/assets/logo1.png"
          alt="Logo"
          class="w-36 h-36 md:w-48 md:h-48"
        />
        <h1 class="text-3xl md:text-5xl font-extrabold text-gray-800 mt-4">
          SeangSangDai
        </h1>
      </div>

      <!-- Open Modal Button -->
      <div class="text-center mb-6">
        <button
          @click="showModal = true"
          class="py-2 px-4 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition duration-300"
        >
          Help
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <!-- Upload Section -->
        <div class="space-y-4">
          <label class="text-lg font-semibold text-gray-700 block">
            Upload MP3 File
          </label>
          <div class="relative">
            <input
              type="file"
              @change="handleFileUpload"
              class="block w-full text-gray-700 py-2 px-3 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        <!-- Language Selection -->
        <div class="space-y-4">
          <label class="text-lg font-semibold text-gray-700 block">
            Select Language
          </label>
          <select
            v-model="selectedLanguage"
            class="block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="en-US">English (US)</option>
            <option value="th-TH">Thai (Thailand)</option>
            <option value="zh-CN">Chinese (Mandarin)</option>
            <option value="ja-JP">Japanese</option>
            <option value="ko-KR">Korean</option>
          </select>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mt-10">
        <!-- Upload Button -->
        <div class="text-center">
          <button
            @click="uploadFileToS3"
            :disabled="isUploading || !file"
            class="w-full py-3 bg-blue-600 text-white font-bold rounded-md shadow-md hover:bg-blue-700 transition duration-300 ease-in-out"
          >
            Upload File
          </button>
        </div>

        <!-- Recording Buttons -->
        <div class="flex justify-center space-x-4">
          <button
            @click="startRecording"
            :disabled="isRecording"
            class="w-full py-3 bg-green-600 text-white font-bold rounded-md shadow-md hover:bg-green-700 transition duration-300 ease-in-out"
          >
            Start Recording
          </button>
          <button
            @click="stopRecording"
            :disabled="!isRecording"
            class="w-full py-3 bg-red-600 text-white font-bold rounded-md shadow-md hover:bg-red-700 transition duration-300 ease-in-out"
          >
            Stop Recording
          </button>
        </div>

        <!-- Transcription Button -->
        <div class="text-center">
          <button
            @click="transcribeFile"
            :disabled="!fileUrl || isTranscribing"
            class="w-full py-3 bg-purple-600 text-white font-bold rounded-md shadow-md hover:bg-purple-700 transition duration-300 ease-in-out"
          >
            Start Transcription
          </button>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mt-10">
        <!-- Get Result Button -->
        <div class="text-center">
          <!-- <button
            @click="getTranscriptionResult"
            :disabled="!jobId || isFetchingResult"
            class="w-full py-3 bg-yellow-600 text-white font-bold rounded-md shadow-md hover:bg-yellow-700 transition duration-300 ease-in-out"
          >
            Get Transcription Result
          </button> -->
        </div>

        <!-- Download PDF Button -->
        <div class="text-center">
          <button
            @click="exportPDF"
            :disabled="!transcriptionResult"
            class="w-full py-3 bg-indigo-600 text-white font-bold rounded-md shadow-md hover:bg-indigo-700 transition duration-300 ease-in-out"
          >
            Download PDF
          </button>
          <p class="mt-2 text-gray-600 text-lg font-semibold italic">Support Only English</p>
        </div>
      </div>

      <!-- Loader Section -->
      <div v-if="isFetchingResult" class="mt-10 text-center">
        <div class="loader"></div>
        <p class="text-gray-500">
          Fetching transcription result... Please wait...
        </p>
      </div>

      <!-- Status Message -->
      <div
        v-if="statusMessage"
        class="mt-10 p-4 bg-gray-100 rounded-lg text-center shadow-md"
      >
        <p class="text-gray-600">{{ statusMessage }}</p>
      </div>

      <!-- Transcription Result Section -->
      <div
        v-if="transcriptionResult"
        class="mt-10 p-6 bg-gray-50 rounded-lg shadow-md"
      >
        <h2 class="text-2xl font-bold text-gray-800 mb-4">
          Transcription Result:
        </h2>
        <p class="text-gray-600">{{ transcriptionResult }}</p>
      </div>

      <!-- Error Message -->
      <p v-if="errorMessage" class="mt-10 text-red-600 text-center">
        {{ errorMessage }}
      </p>

      <!-- Advertisement Section -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mt-12">
        <div class="text-center">
          <a
            href="https://youtu.be/CU77vlEZu5E?si=MDTrosJKwYBZBn0d"
            target="_blank"
          >
            <img
              src="@/assets/1.png"
              alt="Ad Image"
              class="mx-auto w-72 rounded-md shadow-md"
            />
          </a>
        </div>
        <div class="text-center">
          <a
            href="https://youtu.be/CU77vlEZu5E?si=MDTrosJKwYBZBn0d"
            target="_blank"
          >
            <img
              src="@/assets/2.png"
              alt="Ad Image"
              class="mx-auto w-72 rounded-md shadow-md"
            />
          </a>
        </div>
        <div class="text-center">
          <a
            href="https://youtu.be/CU77vlEZu5E?si=MDTrosJKwYBZBn0d"
            target="_blank"
          >
            <img
              src="@/assets/3.png"
              alt="Ad Image"
              class="mx-auto w-72 rounded-md shadow-md"
            />
          </a>
        </div>
      </div>

      <!-- Modal -->
      <div
        v-if="showModal"
        class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50"
      >
        <div class="bg-white rounded-lg p-6 max-w-md mx-auto">
          <h2 class="text-xl font-bold mb-4">
            How to Use the Audio Transcription Service
          </h2>
          <p>1. Upload your MP3 file using the Upload section.</p>
          <p>2. Select the language of the audio from the dropdown menu.</p>
          <p>3. Click the "Upload File" button to upload your audio.</p>
          <p>
            4. If you want to record audio, use the "Start Recording" and "Stop
            Recording" buttons.
          </p>
          <p>
            5. Click "Start Transcription" to transcribe the uploaded or
            recorded audio.
          </p>
          <!-- <p>
            6. Once transcription is done, click "Get Transcription Result" to
            retrieve the result.
          </p> -->
          <p>6. You can download the transcription as a PDF.</p>
          <div class="mt-4 text-right">
            <button
              @click="showModal = false"
              class="py-2 px-4 bg-gray-500 text-white rounded-md hover:bg-gray-600 transition duration-300"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
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
      showModal: false,
      showSuccessMessage: false,
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
          alert("อัปโหลดไฟล์สำเร็จ!"); // เพิ่มการแจ้งเตือนที่นี่
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
          `${process.env.VUE_APP_API_URL}/presigned-url`
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
          `${process.env.VUE_APP_API_URL}/transcription`,
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
            `${process.env.VUE_APP_API_URL}/transcription-status`,
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
          `${process.env.VUE_APP_API_URL}/transcription-result`,
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
  border: 8px solid #f3f3f3; /* Light grey */
  border-top: 8px solid #3498db; /* Blue */
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 2s linear infinite;
  margin: auto;
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
