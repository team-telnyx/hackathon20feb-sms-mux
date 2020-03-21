import request from "superagent";

const API_BASE_URL = "/smsfwd";

const getTeamNumbers = () => {
  let getRequest = request.get(`${API_BASE_URL}/teamnumbers/`);

  return getRequest.then(response => response).catch(console.error);
};

const getMessages = () => {
  let getRequest = request.get(`${API_BASE_URL}/messages/`);

  return getRequest.then(response => response).catch(console.error);
};

const getMessagingProfile = () => {
  let getRequest = request.get(`${API_BASE_URL}/messaging_profile/`);

  return getRequest.then(response => response).catch(console.error);
};

const selectMessagingProfile = profileId => {
  let postRequest = request.post(`${API_BASE_URL}/messaging_profile/`).send({
    profile_id: profileId
  });

  return postRequest.then(response => response).catch(console.error);
};

const addTeamNumber = number => {
  let postRequest = request
    .post(`${API_BASE_URL}/teamnumbers/`)
    .send({ number });

  return postRequest.then(response => response).catch(console.error);
};

const deleteNumber = number => {
  let deleteRequest = request
    .del(`${API_BASE_URL}/teamnumbers/${number}/`)
    .send({ number });

  return deleteRequest.then(response => response).catch(console.error);
};

export default {
  getTeamNumbers,
  getMessagingProfile,
  addTeamNumber,
  selectMessagingProfile,
  deleteNumber,
  getMessages
};
