import request from "superagent";

const API_BASE_URL = "https://api.telnyx.com/v2";
const V2_API_KEY = "<API KEY>";

const withAuthHeaders = request =>
  request.set("Authorization", `Bearer ${V2_API_KEY}`);

const getMessagingProfiles = () => {
  let getRequest = withAuthHeaders(
    request.get(`${API_BASE_URL}/messaging_profiles`)
  );

  return getRequest.then(response => response).catch(console.error);
};

const getProfileNumbers = profileId => {
  let getRequest = withAuthHeaders(
    request.get(`${API_BASE_URL}/messaging_profiles/${profileId}/phone_numbers`)
  );

  return getRequest.then(response => response).catch(console.error);
};

export default {
  getMessagingProfiles,
  getProfileNumbers
};
