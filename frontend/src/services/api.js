
const API_BASE_URL = "/api/v1";

async function handleResponse(response) {
  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error(`Server returned an invalid response (${response.status}).`);
  }

  if (!response.ok) {
    const detail = data.detail;
    throw new Error(
      typeof detail === "string"
        ? detail
        : `Request failed: ${response.status}`
    );
  }

  return data;
}

export async function uploadContract(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(
    `${API_BASE_URL}/investigations/upload?use_ai=false`,
    {
      method: "POST",
      body: formData,
    }
  );

  return handleResponse(response);
}

export async function investigateProperty(firstDocument, secondDocument) {
  const formData = new FormData();
  formData.append("sale_deed", firstDocument);
  formData.append("encumbrance_certificate", secondDocument);

  const response = await fetch(
    `${API_BASE_URL}/investigations/property-investigation`,
    {
      method: "POST",
      body: formData,
    }
  );

  return handleResponse(response);
}
