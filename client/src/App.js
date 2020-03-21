import React from "react";
import styled from "styled-components";

import logo from "./images/logo-dark.svg";
import MessagingProfiles from "./components/MessagingProfiles";
import TeamNumbers from "./components/TeamNumbers";
import Messages from "./components/Messages";

const Wrapper = styled.main`
  min-height: 100vh;
  padding: 1rem 3rem;
  border: 10px solid var(--telnyx-green);
`;

const LogoContainer = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  margin: 2em auto;
`;

const Logo = styled.img`
  display: inline-block;
  width: 200px;
`;

const Tagline = styled.div`
  margin-top: 1em;
  font-size: 14px;
  color: #737373;
  font-style: italic;
`;

const ContentContainer = styled.section`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-gap: 5rem;
`;

function App() {
  return (
    <Wrapper>
      <LogoContainer>
        <Logo src={logo} alt="Telnyx" />
        <Tagline>Florida man in ur cloud texting ur friends!</Tagline>
      </LogoContainer>
      <ContentContainer>
        <TeamNumbers />
        <MessagingProfiles />
        <Messages />
      </ContentContainer>
    </Wrapper>
  );
}

export default App;
