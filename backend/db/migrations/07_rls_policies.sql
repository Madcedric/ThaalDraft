-- 07_rls_policies.sql
-- Enable Row Level Security on user-specific tables
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.exports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.plagiarism_checks ENABLE ROW LEVEL SECURITY;

-- Policy: allow users to SELECT/INSERT/UPDATE their own documents
CREATE POLICY IF NOT EXISTS "documents_owner" ON public.documents
  FOR ALL
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

CREATE POLICY IF NOT EXISTS "jobs_owner" ON public.jobs
  FOR ALL
  USING (EXISTS (SELECT 1 FROM public.documents d WHERE d.id = jobs.document_id AND d.user_id = auth.uid()))
  WITH CHECK (EXISTS (SELECT 1 FROM public.documents d WHERE d.id = jobs.document_id AND d.user_id = auth.uid()));

CREATE POLICY IF NOT EXISTS "exports_owner" ON public.exports
  FOR ALL
  USING (EXISTS (SELECT 1 FROM public.documents d WHERE d.id = exports.document_id AND d.user_id = auth.uid()))
  WITH CHECK (EXISTS (SELECT 1 FROM public.documents d WHERE d.id = exports.document_id AND d.user_id = auth.uid()));

CREATE POLICY IF NOT EXISTS "plagiarism_owner" ON public.plagiarism_checks
  FOR ALL
  USING (EXISTS (SELECT 1 FROM public.documents d WHERE d.id = plagiarism_checks.document_id AND d.user_id = auth.uid()))
  WITH CHECK (EXISTS (SELECT 1 FROM public.documents d WHERE d.id = plagiarism_checks.document_id AND d.user_id = auth.uid()));
