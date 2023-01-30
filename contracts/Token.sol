pragma solidity ^0.6.0;

import "@openzeppelin/math/SafeMath.sol";
import "@openzeppelin/token/ERC20/ERC20.sol";

// Base token implementation
contract Token is ERC20 {

    using SafeMath for uint256;

    constructor (
        string memory _name,
        address _mintAddress, 
        uint256 _mintAmount
    ) ERC20(_name, _name) public {
        _mint(_mintAddress,_mintAmount);
    }   

}
