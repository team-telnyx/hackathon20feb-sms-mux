import React from "react";
import PropTypes from "prop-types";
import { Card, Button } from "antd";
import styled from "styled-components";

import telnyxService from "../../../services/telnyx";

const Wrapper = styled.section`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min-content, 300px));
  grid-gap: 1em;
`;

const MessagingProfile = ({ profileId }) => {
  const [profileNumbers, setProfileNumbers] = React.useState([]);
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    setIsLoading(true);
    telnyxService
      .getProfileNumbers(profileId)
      .then(response => {
        response.body && setProfileNumbers(response.body.data);
        setIsLoading(false);
      })
      .catch(console.error);
  }, [profileId]);

  return (
    <Wrapper>
      <Card size="small" title="Phone Numbers">
        {isLoading && "loading..."}
        {!isLoading &&
          profileNumbers.length < 1 &&
          "No numbers assigned to this profile."}
        {profileNumbers.map(number => (
          <div key={number.id}>{number.phone_number}</div>
        ))}
      </Card>
    </Wrapper>
  );
};

MessagingProfile.propTypes = {
  profileId: PropTypes.string
};

export default MessagingProfile;
