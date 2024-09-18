<template>
  <div id="app" class="container mx-auto p-6">
    <h1 class="text-4xl font-bold text-center text-blue-600 mb-6">
      Upload or Record Audio
    </h1>

    <!-- อัปโหลดไฟล์ -->
    <div class="mb-4">
      <label class="block text-lg font-medium text-gray-700 mb-2"
        >Upload MP3 File:</label
      >
      <input
        type="file"
        @change="handleFileUpload"
        class="block w-full text-gray-600 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-600 hover:file:bg-blue-100"
      />
    </div>

    <!-- เลือกภาษา -->
    <div class="mb-4">
      <label class="block text-lg font-medium text-gray-700 mb-2" for="language"
        >Select Language:</label
      >
      <select
        v-model="selectedLanguage"
        class="block w-full px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
      >
        <option value="en-US">English (US)</option>
        <option value="th-TH">Thai (Thailand)</option>
        <option value="zh-CN">Chinese (Mandarin)</option>
        <option value="ja-JP">Japanese</option>
        <option value="ko-KR">Korean</option>
      </select>
    </div>

    <!-- ปุ่มอัปโหลด -->
    <div class="mb-6 text-center">
      <button
        @click="uploadFileToS3"
        :disabled="isUploading || !file"
        class="px-4 py-2 bg-blue-600 text-white font-semibold rounded-md shadow hover:bg-blue-700 disabled:opacity-50"
      >
        Upload File
      </button>
    </div>

    <!-- อัดเสียง -->
    <div class="mb-6 text-center">
      <button
        @click="startRecording"
        :disabled="isRecording"
        class="px-4 py-2 bg-green-600 text-white font-semibold rounded-md shadow hover:bg-green-700 disabled:opacity-50"
      >
        Start Recording
      </button>
      <button
        @click="stopRecording"
        :disabled="!isRecording"
        class="ml-4 px-4 py-2 bg-red-600 text-white font-semibold rounded-md shadow hover:bg-red-700 disabled:opacity-50"
      >
        Stop Recording
      </button>
    </div>

    <!-- ปุ่มเริ่มถอดความ -->
    <div class="mb-6 text-center">
      <button
        @click="transcribeFile"
        :disabled="!fileUrl || isTranscribing"
        class="px-4 py-2 bg-purple-600 text-white font-semibold rounded-md shadow hover:bg-purple-700 disabled:opacity-50"
      >
        Start Transcription
      </button>
    </div>

    <!-- ปุ่มรับผลลัพธ์ -->
    <div class="mb-6 text-center">
      <button
        @click="getTranscriptionResult"
        :disabled="!jobId || isFetchingResult"
        class="px-4 py-2 bg-yellow-600 text-white font-semibold rounded-md shadow hover:bg-yellow-700 disabled:opacity-50"
      >
        Get Transcription Result
      </button>
    </div>

    <!-- แสดงผลลัพธ์การถอดความ -->
    <div
      v-if="transcriptionResult"
      class="bg-gray-100 p-4 rounded-lg shadow-md"
    >
      <h2 class="text-lg font-bold text-gray-700 mb-2">
        Transcription Result:
      </h2>
      <p class="text-gray-600">{{ transcriptionResult }}</p>
    </div>

    <!-- ข้อความแสดงข้อผิดพลาด -->
    <p v-if="errorMessage" class="text-red-600 text-center mt-4">
      {{ errorMessage }}
    </p>
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
      isRecording: false,
      mediaRecorder: null,
      audioChunks: [],
      file: null,
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
        this.errorMessage = error.message;
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
        console.error("Error starting transcription:", error);
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
        console.error("Error fetching transcription result:", error);
      } finally {
        this.isFetchingResult = false;
      }
    },

    startRecording() {
      this.isRecording = true;
      this.audioChunks = [];

      navigator.mediaDevices
        .getUserMedia({ audio: true })
        .then((stream) => {
          this.mediaRecorder = new MediaRecorder(stream);
          this.mediaRecorder.ondataavailable = (event) => {
            this.audioChunks.push(event.data);
          };
          this.mediaRecorder.start();
        })
        .catch((error) => {
          this.errorMessage = "Could not start recording: " + error.message;
          console.error("Recording error:", error);
        });
    },

    stopRecording() {
      if (this.mediaRecorder) {
        this.mediaRecorder.stop();
        this.isRecording = false;
        this.mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(this.audioChunks, { type: "audio/mpeg" });
          this.file = new File([audioBlob], "recording.mp3", {
            type: "audio/mpeg",
          });
          await this.uploadFileToS3();
        };
      }
    },
  },
};
</script>

<style scoped>
/* ไม่มี CSS แบบกำหนดเองเพิ่มเติม เพราะใช้ Tailwind CSS */
</style>
