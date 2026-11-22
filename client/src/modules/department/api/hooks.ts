import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { http } from "../../../lib/http";
import type {
  SeminarRequest,
  GraduateSeminar,
  SubmitSeminarRequestInput,
  ScheduleSeminarInput,
  ThesisSupervisorAllocation,
  TAAllocation,
  DepartmentAnnouncement,
} from "./types";

interface Page<T> {
  count: number;
  results: T[];
}

const KEY = "department";

export const keys = {
  requests: () => [KEY, "requests"] as const,
  request: (id: number) => [KEY, "request", id] as const,
  pending: () => [KEY, "pending"] as const,
  seminars: () => [KEY, "seminars"] as const,
  seminar: (id: number) => [KEY, "seminar", id] as const,
  taAllocations: () => [KEY, "ta-allocations"] as const,
  supervisorAllocations: () => [KEY, "supervisor-allocations"] as const,
  announcements: () => [KEY, "announcements"] as const,
};

function invalidateAll(qc: ReturnType<typeof useQueryClient>) {
  qc.invalidateQueries({ queryKey: [KEY] });
}

// -- Seminar Requests (OA-UC-51) ---------------------------------------------

export function useSeminarRequests() {
  return useQuery({
    queryKey: keys.requests(),
    queryFn: async () => {
      const res = await http.get<Page<SeminarRequest> | SeminarRequest[]>("/department/requests/");
      const data = res.data;
      return Array.isArray(data) ? data : data.results;
    },
  });
}

export function usePendingSeminars() {
  return useQuery({
    queryKey: keys.pending(),
    queryFn: async () => {
      const res = await http.get<Page<SeminarRequest> | SeminarRequest[]>("/department/pending/");
      const data = res.data;
      return Array.isArray(data) ? data : data.results;
    },
  });
}

export function useScheduledSeminars(department: string = "") {
  return useQuery({
    queryKey: [...keys.seminars(), department],
    queryFn: async () => {
      const url = department
        ? `/department/seminars/?department=${encodeURIComponent(department)}`
        : "/department/seminars/";
      const res = await http.get<Page<GraduateSeminar> | GraduateSeminar[]>(url);
      const data = res.data;
      return Array.isArray(data) ? data : data.results;
    },
  });
}

export function useSubmitSeminarRequest() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: SubmitSeminarRequestInput) =>
      http.post<SeminarRequest>("/department/requests/", data).then((res) => res.data),
    onSuccess: () => invalidateAll(qc),
  });
}

export function useScheduleSeminar() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: ScheduleSeminarInput }) =>
      http.post<GraduateSeminar>(`/department/requests/${id}/schedule/`, data).then((res) => res.data),
    onSuccess: () => invalidateAll(qc),
  });
}

export function useRejectSeminar() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, reason }: { id: number; reason: string }) =>
      http.post<SeminarRequest>(`/department/requests/${id}/reject/`, { reason }).then((res) => res.data),
    onSuccess: () => invalidateAll(qc),
  });
}

export function useCancelSeminar() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) =>
      http.delete<SeminarRequest>(`/department/requests/${id}/`).then((res) => res.data),
    onSuccess: () => invalidateAll(qc),
  });
}

// -- Allocations (AFR-OAP-043, AFR-OAP-044) -----------------------------------

export function useTAAllocations() {
  return useQuery({
    queryKey: keys.taAllocations(),
    queryFn: async () => {
      const res = await http.get<Page<TAAllocation> | TAAllocation[]>("/department/allocations/ta/");
      const data = res.data;
      return Array.isArray(data) ? data : data.results;
    },
  });
}

export function useCreateTAAllocation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<TAAllocation>) =>
      http.post<TAAllocation>("/department/allocations/ta/", data).then((res) => res.data),
    onSuccess: () => invalidateAll(qc),
  });
}

export function useSupervisorAllocations() {
  return useQuery({
    queryKey: keys.supervisorAllocations(),
    queryFn: async () => {
      const res = await http.get<Page<ThesisSupervisorAllocation> | ThesisSupervisorAllocation[]>(
        "/department/allocations/supervisors/"
      );
      const data = res.data;
      return Array.isArray(data) ? data : data.results;
    },
  });
}

export function useCreateSupervisorAllocation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<ThesisSupervisorAllocation>) =>
      http.post<ThesisSupervisorAllocation>("/department/allocations/supervisors/", data).then((res) => res.data),
    onSuccess: () => invalidateAll(qc),
  });
}

// -- Announcements ------------------------------------------------------------

export function useAnnouncements() {
  return useQuery({
    queryKey: keys.announcements(),
    queryFn: async () => {
      const res = await http.get<Page<DepartmentAnnouncement> | DepartmentAnnouncement[]>(
        "/department/announcements/"
      );
      const data = res.data;
      return Array.isArray(data) ? data : data.results;
    },
  });
}

export function useCreateAnnouncement() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<DepartmentAnnouncement>) =>
      http.post<DepartmentAnnouncement>("/department/announcements/", data).then((res) => res.data),
    onSuccess: () => invalidateAll(qc),
  });
}

