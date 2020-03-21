import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";
import { Table, Switch } from "antd";

import telnyxService from "../../services/telnyx";
import floridaManService from "../../services/floridaMan";
import MessagingProfile from "./MessagingProfile";

const Wrapper = styled.section``;

const Heading = styled.h2``;

const MessagingProfiles = () => {
  const [profiles, setProfiles] = React.useState([]);
  const [selectedProfile, setSelectedProfile] = React.useState([]);
  const tableColumns = [
    {
      title: "Name",
      dataIndex: "name",
      key: "name"
    },
    {
      title: "Selected",
      dataIndex: "selected",
      key: "selected",
      render: profileId => (
        <Switch
          checked={profileId === selectedProfile}
          onChange={() => handleSelectProfile(profileId)}
        />
      )
    }
  ];

  function handleSelectProfile(profileId) {
    floridaManService
      .selectMessagingProfile(profileId)
      .then(getSelectedMessagingProfile);
  }

  React.useEffect(() => {
    getTelnyxMessagingProfiles();
    getSelectedMessagingProfile();
  }, []);

  function getSelectedMessagingProfile() {
    floridaManService
      .getMessagingProfile()
      .then(response => {
        if (!response.body) return;

        const profile = response.body;

        setSelectedProfile(profile.profile_id);
      })
      .catch(console.error);
  }

  function getTelnyxMessagingProfiles() {
    telnyxService
      .getMessagingProfiles()
      .then(response => {
        if (!response.body) return;

        const profiles = response.body;

        setProfiles(response.body.data);
      })
      .catch(console.error);
  }

  const tableData = React.useMemo(() => {
    return profiles.map(profile => ({
      key: profile.id,
      name: profile.name,
      selected: profile.id,
      id: profile.id
    }));
  }, [profiles]);

  return (
    <Wrapper>
      <Heading>Messaging Profiles</Heading>
      <h4>Select the profile that will forward messages to the Team Numbers</h4>

      <Table
        dataSource={tableData}
        columns={tableColumns}
        pagination={false}
        expandedRowRender={profile => (
          <MessagingProfile profileId={profile.id} />
        )}
      />
    </Wrapper>
  );
};

MessagingProfiles.propTypes = {};

export default MessagingProfiles;
