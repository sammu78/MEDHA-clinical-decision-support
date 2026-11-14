import type {
  PatientAssessmentRequest,
  AssessmentResponse,
  SupportedCase,
  EvidenceSource,
  ClinicalCase,
  IndianMedicineProduct,
  AuditSummary,
  EvidenceSearchResponse,
  RAGQueryResponse,
  DashboardMetrics
} from "../types";

const rawBaseUrl = import.meta.env.VITE_API_BASE_URL;
const API_BASE_URL =
  rawBaseUrl !== undefined && rawBaseUrl !== ""
    ? rawBaseUrl.startsWith("http://") || rawBaseUrl.startsWith("https://")
      ? rawBaseUrl
      : `https://${rawBaseUrl}`
    : import.meta.env.DEV
    ? "http://127.0.0.1:8000"
    : "";

export async function checkBackendHealth(): Promise<{ status: string; service: string }> {
  const res = await fetch(`${API_BASE_URL}/health`);
  if (!res.ok) {
    throw new Error(`Health check failed: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchSupportedCases(): Promise<SupportedCase[]> {
  const res = await fetch(`${API_BASE_URL}/supported-cases`);
  if (!res.ok) {
    throw new Error(`Failed to load supported cases: ${res.statusText}`);
  }
  return res.json();
}

export async function assessPatient(request: PatientAssessmentRequest): Promise<AssessmentResponse> {
  const res = await fetch(`${API_BASE_URL}/assess`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request)
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Assessment failed: ${res.status} - ${errorText}`);
  }
  return res.json();
}

export async function fetchEvidenceSource(sourceId: string): Promise<EvidenceSource> {
  const res = await fetch(`${API_BASE_URL}/sources/${sourceId}`);
  if (!res.ok) {
    throw new Error(`Failed to load evidence source: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchModelEvaluationInfo(caseId: string): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/model-info/${caseId}`);
  if (!res.ok) {
    throw new Error(`Failed to load model info: ${res.statusText}`);
  }
  return res.json();
}

// Clinical Cases API
export async function listClinicalCases(doctorId: string = "dr_session"): Promise<ClinicalCase[]> {
  const res = await fetch(`${API_BASE_URL}/cases?doctor_id=${encodeURIComponent(doctorId)}`);
  if (!res.ok) {
    throw new Error(`Failed to list cases: ${res.statusText}`);
  }
  return res.json();
}

export async function createClinicalCase(caseId?: string, doctorId: string = "dr_session"): Promise<ClinicalCase> {
  const res = await fetch(`${API_BASE_URL}/cases`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ case_id: caseId, doctor_id: doctorId })
  });
  if (!res.ok) {
    throw new Error(`Failed to create case: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchClinicalCase(caseId: string): Promise<ClinicalCase> {
  const res = await fetch(`${API_BASE_URL}/cases/${caseId}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch case ${caseId}: ${res.statusText}`);
  }
  return res.json();
}

export async function updatePatientData(caseId: string, patientData: Record<string, any>): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/cases/${caseId}/patient`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(patientData)
  });
  if (!res.ok) {
    throw new Error(`Failed to update patient data: ${res.statusText}`);
  }
  return res.json();
}

export async function assessCase(caseId: string): Promise<AssessmentResponse> {
  const res = await fetch(`${API_BASE_URL}/cases/${caseId}/assess`, {
    method: "POST"
  });
  if (!res.ok) {
    throw new Error(`Failed to assess case ${caseId}: ${res.statusText}`);
  }
  return res.json();
}

export async function approveTreatmentPlan(caseId: string, notes: string = "Approved by doctor"): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/cases/${caseId}/approve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ notes })
  });
  if (!res.ok) {
    throw new Error(`Failed to approve plan: ${res.statusText}`);
  }
  return res.json();
}

export async function exportDraftAssessment(caseId: string): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/cases/${caseId}/export`);
  if (!res.ok) {
    throw new Error(`Failed to export draft: ${res.statusText}`);
  }
  return res.json();
}

// Indian Medicines API
export async function searchIndianMedicines(
  q: string = "",
  generic?: string,
  formulation?: string,
  limit: number = 20,
  offset: number = 0
): Promise<IndianMedicineProduct[]> {
  let url = `${API_BASE_URL}/medicines/search?limit=${limit}&offset=${offset}`;
  if (q) url += `&q=${encodeURIComponent(q)}`;
  if (generic) url += `&generic=${encodeURIComponent(generic)}`;
  if (formulation) url += `&formulation=${encodeURIComponent(formulation)}`;
  
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Failed to search Indian medicines: ${res.statusText}`);
  }
  return res.json();
}

export async function matchIndianProducts(
  generic: string,
  strength?: string,
  route?: string
): Promise<IndianMedicineProduct[]> {
  let url = `${API_BASE_URL}/medicines/match?generic=${encodeURIComponent(generic)}`;
  if (strength) url += `&strength=${encodeURIComponent(strength)}`;
  if (route) url += `&route=${encodeURIComponent(route)}`;

  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Failed to match Indian products: ${res.statusText}`);
  }
  return res.json();
}

// Evidence Upload
export async function uploadEvidenceDocument(doc: {
  title: string;
  organization: string;
  url: string;
  disease_tag: string;
  content: string;
}): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/documents`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(doc)
  });
  if (!res.ok) {
    throw new Error(`Failed to upload document: ${res.statusText}`);
  }
  return res.json();
}

// Data Audit
export async function fetchDataAudit(): Promise<AuditSummary> {
  const res = await fetch(`${API_BASE_URL}/audit`);
  if (!res.ok) {
    throw new Error(`Failed to load data audit: ${res.statusText}`);
  }
  return res.json();
}

// SSE Streaming Client
export async function streamCaseEvents(
  caseId: string,
  message: string,
  callbacks: {
    onStatus?: (status: string) => void;
    onPatientUpdate?: (confirmations: string[], patientData: any) => void;
    onAssessment?: (asmt: AssessmentResponse) => void;
    onToken?: (token: string) => void;
    onDone?: (msgId: string) => void;
    onError?: (err: Error) => void;
  }
): Promise<void> {
  const url = `${API_BASE_URL}/cases/${caseId}/stream?message=${encodeURIComponent(message)}`;
  
  try {
    const response = await fetch(url);
    if (!response.ok || !response.body) {
      throw new Error(`SSE stream connection failed: ${response.status} ${response.statusText}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n\n");
      buffer = lines.pop() || "";

      for (const block of lines) {
        if (!block.trim()) continue;
        const blockLines = block.split("\n");
        let eventType = "message";
        let dataStr = "";

        for (const line of blockLines) {
          if (line.startsWith("event: ")) {
            eventType = line.replace("event: ", "").trim();
          } else if (line.startsWith("data: ")) {
            dataStr = line.replace("data: ", "").trim();
          }
        }

        if (!dataStr) continue;

        try {
          const data = JSON.parse(dataStr);
          if (eventType === "status" && callbacks.onStatus) {
            callbacks.onStatus(data.status);
          } else if (eventType === "patient_update" && callbacks.onPatientUpdate) {
            callbacks.onPatientUpdate(data.confirmations, data.patient_data);
          } else if (eventType === "assessment" && callbacks.onAssessment) {
            callbacks.onAssessment(data);
          } else if (eventType === "token" && callbacks.onToken) {
            callbacks.onToken(data.text);
          } else if (eventType === "done" && callbacks.onDone) {
            callbacks.onDone(data.message_id);
          }
        } catch (e) {
          console.warn("Failed to parse SSE JSON chunk:", dataStr, e);
        }
      }
    }
  } catch (err: any) {
    if (callbacks.onError) {
      callbacks.onError(err);
    } else {
      console.error("SSE stream error:", err);
    }
  }
}

export async function searchEvidenceLibrary(
  query: string,
  diseaseTag?: string,
  medicineTag?: string,
  topK: number = 5
): Promise<EvidenceSearchResponse> {
  const params = new URLSearchParams({
    q: query,
    top_k: topK.toString()
  });
  if (diseaseTag) params.append("disease_tag", diseaseTag);
  if (medicineTag) params.append("medicine_tag", medicineTag);

  const res = await fetch(`${API_BASE_URL}/evidence/search?${params.toString()}`);
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Evidence search failed: ${res.status} - ${errorText}`);
  }
  return res.json();
}

export async function askEvidenceQuestion(
  query: string,
  diseaseTag?: string,
  medicineTag?: string,
  topK: number = 3
): Promise<RAGQueryResponse> {
  const res = await fetch(`${API_BASE_URL}/evidence/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query,
      disease_tag: diseaseTag || undefined,
      medicine_tag: medicineTag || undefined,
      top_k: topK
    })
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`RAG QA query failed: ${res.status} - ${errorText}`);
  }
  return res.json();
}

export async function fetchDashboardMetrics(): Promise<DashboardMetrics> {
  const res = await fetch(`${API_BASE_URL}/dashboard/metrics`);
  if (!res.ok) {
    throw new Error(`Failed to load dashboard metrics: ${res.statusText}`);
  }
  return res.json();
}

