import { GenerateButton } from "./components/GenerateButton";
import { Header } from "./components/Header";
import { StatusAlert } from "./components/StatusAlert";
import { ZipDropzone } from "./components/ZipDropzone";
import { ZipFileList } from "./components/ZipFileList";
import { useFiscalUpload } from "./hooks/useFiscalUpload";
import "./App.css";

export function App() {
  const {
    files,
    isLoading,
    errorMsg,
    successMsg,
    remainingSlots,
    isFull,
    addFiles,
    removeFile,
    submitReports,
  } = useFiscalUpload();

  return (
    <main className="page-wrapper">
      <section className="card">
        <Header
          title="TRM Fiscal"
          subtitle="Envie de 1 a 3 lotes (.zip) com XMLs fiscais para gerar os relatórios em PDF."
        />

        <ZipDropzone
          isFull={isFull}
          disabled={isLoading}
          remainingSlots={remainingSlots}
          onFilesAdded={addFiles}
        />

        <ZipFileList
          files={files}
          disabled={isLoading}
          onRemoveFile={removeFile}
        />

        <StatusAlert type="error" message={errorMsg} />
        <StatusAlert type="success" message={successMsg} />

        <GenerateButton
          isLoading={isLoading}
          disabled={files.length === 0}
          onClick={submitReports}
        />
      </section>
    </main>
  );
}

export default App;