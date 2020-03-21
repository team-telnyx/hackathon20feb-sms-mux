import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";
import { List, Button } from "antd";

import floridaManService from "../../services/floridaMan";
import AddNumbersForm from "./AddNumbersForm";
import { formatPhoneNumber } from "../../utils";

const Wrapper = styled.section``;

const Heading = styled.h2``;

const ShowFormButton = styled(Button)`
  width: 100%;
  margin-top: 1rem;
`;

export const TeamNumbersContext = React.createContext();

const TeamNumbers = () => {
  const [teamNumbers, setTeamNumbers] = React.useState([]);
  const [isAddingNumbers, setIsAddingNumbers] = React.useState(false);

  React.useEffect(() => {
    getTeamNumbers();
  }, []);

  function getTeamNumbers() {
    floridaManService
      .getTeamNumbers()
      .then(response => {
        setTeamNumbers(response.body || []);
      })
      .catch(console.error);
  }

  function deleteNumber(phoneNumber) {
    floridaManService
      .deleteNumber(phoneNumber)
      .then(getTeamNumbers)
      .catch(console.error);
  }

  return (
    <TeamNumbersContext.Provider
      value={{
        setIsAddingNumbers,
        fetchNumbers: getTeamNumbers
      }}
    >
      <Wrapper>
        <Heading>Team Numbers</Heading>
        <h4>These numbers get messaged forwarded to them</h4>

        <List
          size="small"
          bordered
          dataSource={teamNumbers}
          renderItem={phoneNumber => (
            <List.Item
              extra={
                <Button
                  icon="delete"
                  type="danger"
                  onClick={() => deleteNumber(phoneNumber.number)}
                />
              }
            >
              {formatPhoneNumber(phoneNumber.number)}
            </List.Item>
          )}
        />

        {!isAddingNumbers && (
          <ShowFormButton
            icon="plus"
            onClick={() => setIsAddingNumbers(!isAddingNumbers)}
          >
            Add Number(s)
          </ShowFormButton>
        )}

        {isAddingNumbers && <AddNumbersForm />}
      </Wrapper>
    </TeamNumbersContext.Provider>
  );
};

TeamNumbers.propTypes = {};

export default TeamNumbers;
